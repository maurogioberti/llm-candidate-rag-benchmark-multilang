import json
import httpx
from pathlib import Path
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod


OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OLLAMA_GENERATE_ENDPOINT = "/api/generate"

EVALUATION_PROMPT_PATH = Path(__file__).parent.parent.parent / "data" / "prompts" / "evaluation_judge.md"

WINNER_DOTNET = "dotnet"
WINNER_PYTHON = "python"
WINNER_TIE = "tie"

_PROMPT_TEMPLATE_CACHE: Optional[str] = None


def _load_prompt_template() -> str:
    """Load evaluation prompt template from file (cached)."""
    global _PROMPT_TEMPLATE_CACHE
    
    if _PROMPT_TEMPLATE_CACHE is None:
        _PROMPT_TEMPLATE_CACHE = EVALUATION_PROMPT_PATH.read_text(encoding="utf-8")
    
    return _PROMPT_TEMPLATE_CACHE


def determine_winner(dotnet_score: float, python_score: float, tolerance: float) -> str:
    """Determine winner from scores with configurable tie tolerance."""
    diff = abs(dotnet_score - python_score)
    
    if diff <= tolerance:
        return WINNER_TIE
    
    return WINNER_DOTNET if dotnet_score > python_score else WINNER_PYTHON


def _build_standard_evaluation_prompt(
    question: str,
    dotnet_response: str,
    python_response: str,
    expected_criteria: List[str]
) -> str:
    """Build evaluation prompt from template file."""
    template = _load_prompt_template()
    return template.format(
        question=question,
        dotnet_response=dotnet_response,
        python_response=python_response
    )


class ScoringStrategy(ABC):
    @abstractmethod
    async def evaluate(
        self,
        question: str,
        dotnet_response: str,
        python_response: str,
        expected_criteria: List[str]
    ) -> Dict[str, Any]:
        pass


class OpenAIJudge(ScoringStrategy):
    def __init__(self, api_key: str, model: str, temperature: float, timeout: float):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
    
    async def evaluate(
        self,
        question: str,
        dotnet_response: str,
        python_response: str,
        expected_criteria: List[str]
    ) -> Dict[str, Any]:
        prompt = _build_standard_evaluation_prompt(
            question, dotnet_response, python_response, expected_criteria
        )
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "temperature": self.temperature,
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a strict evaluator. Respond ONLY valid JSON matching the schema."
                    },
                    {"role": "user", "content": prompt},
                ],
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(OPENAI_API_URL, headers=headers, json=payload)
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"].strip()
                return json.loads(content)
                
        except Exception as e:
            raise RuntimeError(f"OpenAI judge evaluation failed: {e}") from e


class OllamaJudge(ScoringStrategy):
    def __init__(self, host: str, model: str, temperature: float, timeout: float):
        self.host = host.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
    
    async def evaluate(
        self,
        question: str,
        dotnet_response: str,
        python_response: str,
        expected_criteria: List[str]
    ) -> Dict[str, Any]:
        prompt = _build_standard_evaluation_prompt(
            question, dotnet_response, python_response, expected_criteria
        )
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt + "\n\nRespond ONLY with a valid JSON object.",
                "temperature": self.temperature,
                "stream": False,
            }
            
            url = f"{self.host}{OLLAMA_GENERATE_ENDPOINT}"
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                text = response.json().get("response", "").strip()
                return json.loads(text)
                
        except Exception as e:
            raise RuntimeError(f"Ollama judge evaluation failed: {e}") from e


class HeuristicJudge(ScoringStrategy):
    def __init__(self, tie_tolerance: float):
        self.tie_tolerance = tie_tolerance
    
    async def evaluate(
        self,
        question: str,
        dotnet_response: str,
        python_response: str,
        expected_criteria: List[str]
    ) -> Dict[str, Any]:
        dotnet_score = self._calculate_score(dotnet_response, expected_criteria)
        python_score = self._calculate_score(python_response, expected_criteria)
        
        winner = determine_winner(dotnet_score, python_score, self.tie_tolerance)
        
        return {
            "dotnet_score": round(dotnet_score, 2),
            "python_score": round(python_score, 2),
            "winner": winner,
            "comment": "Heuristic baseline judge used (no external LLM).",
        }
    
    def _calculate_score(self, response: str, criteria: List[str]) -> float:
        if not response or response.lower().startswith("error:"):
            return 1.0
        
        text = response.lower()
        
        coverage_score = self._calculate_coverage(text, criteria)
        length_score = self._calculate_length_score(len(response))
        clarity_score = self._calculate_clarity_score(text)
        actionability_score = self._calculate_actionability_score(text)
        ranking_score = self._calculate_ranking_score(text)
        
        raw_score = (
            3.5 * coverage_score +
            2.5 * length_score +
            1.5 * clarity_score +
            1.25 * actionability_score +
            1.25 * ranking_score
        )
        
        return max(0.0, min(10.0, raw_score))
    
    def _calculate_coverage(self, text: str, criteria: List[str]) -> float:
        if not criteria:
            return 0.0
        
        normalized_criteria = [c.lower() for c in criteria]
        hits = sum(1 for criterion in normalized_criteria if criterion in text)
        return hits / len(normalized_criteria)
    
    def _calculate_length_score(self, length: int) -> float:
        if length > 800:
            return 1.0
        elif length > 300:
            return 0.7
        elif length > 120:
            return 0.4
        else:
            return 0.1
    
    def _calculate_clarity_score(self, text: str) -> float:
        if any(marker in text for marker in ["\n- ", "\n* ", "1.", "2.", "3."]):
            return 0.8
        elif "\n\n" in text:
            return 0.5
        else:
            return 0.2
    
    def _calculate_actionability_score(self, text: str) -> float:
        actionable_keywords = ["recommend", "next step", "should", "interview", "hire"]
        return 1.0 if any(keyword in text for keyword in actionable_keywords) else 0.2
    
    def _calculate_ranking_score(self, text: str) -> float:
        ranking_keywords = ["rank", "ranking", "top", "1.", "2.", "3."]
        return 1.0 if any(keyword in text for keyword in ranking_keywords) else 0.2


class ScoringStrategyFactory:
    @staticmethod
    def create(
        provider: str,
        temperature: float,
        tie_tolerance: float,
        heuristic_tie_tolerance: float,
        openai_timeout: float,
        ollama_timeout: float,
        openai_api_key: str = None,
        openai_model: str = None,
        ollama_host: str = None,
        ollama_model: str = None
    ) -> ScoringStrategy:
        if provider == "openai" and openai_api_key:
            return OpenAIJudge(openai_api_key, openai_model, temperature, openai_timeout)
        
        if provider == "ollama":
            return OllamaJudge(ollama_host, ollama_model, temperature, ollama_timeout)
        
        return HeuristicJudge(heuristic_tie_tolerance)