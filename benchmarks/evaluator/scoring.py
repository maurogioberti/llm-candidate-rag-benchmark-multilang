import json
import httpx
from typing import Dict, Any, List
from abc import ABC, abstractmethod


OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_TIMEOUT = 60.0
OLLAMA_GENERATE_ENDPOINT = "/api/generate"
OLLAMA_TIMEOUT = 120.0
HEURISTIC_TIE_TOLERANCE = 0.25


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
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
    
    async def evaluate(
        self,
        question: str,
        dotnet_response: str,
        python_response: str,
        expected_criteria: List[str]
    ) -> Dict[str, Any]:
        prompt = self._build_evaluation_prompt(
            question, dotnet_response, python_response, expected_criteria
        )
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a strict evaluator. Respond ONLY valid JSON matching the schema."
                    },
                    {"role": "user", "content": prompt},
                ],
            }
            
            async with httpx.AsyncClient(timeout=OPENAI_TIMEOUT) as client:
                response = await client.post(OPENAI_API_URL, headers=headers, json=payload)
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"].strip()
                return json.loads(content)
                
        except Exception as e:
            print(f"⚠️  OpenAI error: {e}. Falling back to heuristic.")
            heuristic = HeuristicJudge()
            return await heuristic.evaluate(question, dotnet_response, python_response, expected_criteria)
    
    def _build_evaluation_prompt(
        self,
        question: str,
        dotnet_response: str,
        python_response: str,
        expected_criteria: List[str]
    ) -> str:
        return f"""
You are an HR expert evaluating chatbot responses for candidate selection.

QUESTION: {question}

.NET RESPONSE:
{dotnet_response}

PYTHON RESPONSE:
{python_response}

Evaluate both responses according to these criteria:
1. Accuracy: Is the response accurate and relevant?
2. Completeness: Does it include all expected criteria?
3. Clarity: Is it clear and easy to understand?
4. Actionability: Does it provide actionable information for HR?
5. Ranking Quality: Is the ranking/ordering logical and justified?

Scoring Scale:
- 0-2: Very poor - Does not answer the question
- 3-4: Poor - Partial or incorrect response
- 5-6: Acceptable - Basic but incomplete response
- 7-8: Good - Complete and accurate response
- 9-10: Excellent - Exceptional and detailed response

Respond in JSON format:
{{
    "dotnet_score": <score 0-10>,
    "python_score": <score 0-10>,
    "winner": "<dotnet|python|tie>",
    "comment": "<detailed explanation of the evaluation>"
}}
"""


class OllamaJudge(ScoringStrategy):
    def __init__(self, host: str, model: str):
        self.host = host.rstrip("/")
        self.model = model
    
    async def evaluate(
        self,
        question: str,
        dotnet_response: str,
        python_response: str,
        expected_criteria: List[str]
    ) -> Dict[str, Any]:
        prompt = self._build_evaluation_prompt(
            question, dotnet_response, python_response, expected_criteria
        )
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt + "\n\nRespond ONLY with a valid JSON object.",
                "stream": False,
            }
            
            url = f"{self.host}{OLLAMA_GENERATE_ENDPOINT}"
            async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                text = response.json().get("response", "").strip()
                return json.loads(text)
                
        except Exception as e:
            print(f"⚠️  Ollama error: {e}. Falling back to heuristic.")
            heuristic = HeuristicJudge()
            return await heuristic.evaluate(question, dotnet_response, python_response, expected_criteria)
    
    def _build_evaluation_prompt(
        self,
        question: str,
        dotnet_response: str,
        python_response: str,
        expected_criteria: List[str]
    ) -> str:
        return f"""
You are an HR expert evaluating chatbot responses for candidate selection.

QUESTION: {question}

.NET RESPONSE:
{dotnet_response}

PYTHON RESPONSE:
{python_response}

Evaluate both responses according to these criteria:
1. Accuracy: Is the response accurate and relevant?
2. Completeness: Does it include all expected criteria?
3. Clarity: Is it clear and easy to understand?
4. Actionability: Does it provide actionable information for HR?
5. Ranking Quality: Is the ranking/ordering logical and justified?

Scoring Scale:
- 0-2: Very poor - Does not answer the question
- 3-4: Poor - Partial or incorrect response
- 5-6: Acceptable - Basic but incomplete response
- 7-8: Good - Complete and accurate response
- 9-10: Excellent - Exceptional and detailed response

Respond in JSON format:
{{
    "dotnet_score": <score 0-10>,
    "python_score": <score 0-10>,
    "winner": "<dotnet|python|tie>",
    "comment": "<detailed explanation of the evaluation>"
}}
"""


class HeuristicJudge(ScoringStrategy):
    async def evaluate(
        self,
        question: str,
        dotnet_response: str,
        python_response: str,
        expected_criteria: List[str]
    ) -> Dict[str, Any]:
        dotnet_score = self._calculate_score(dotnet_response, expected_criteria)
        python_score = self._calculate_score(python_response, expected_criteria)
        
        winner = self._determine_winner(dotnet_score, python_score)
        
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
    
    def _determine_winner(self, dotnet_score: float, python_score: float) -> str:
        diff = abs(dotnet_score - python_score)
        
        if diff <= HEURISTIC_TIE_TOLERANCE:
            return "tie"
        
        return "dotnet" if dotnet_score > python_score else "python"


class ScoringStrategyFactory:
    @staticmethod
    def create(
        provider: str,
        openai_api_key: str = None,
        openai_model: str = None,
        ollama_host: str = None,
        ollama_model: str = None
    ) -> ScoringStrategy:
        if provider == "openai" and openai_api_key:
            return OpenAIJudge(openai_api_key, openai_model)
        
        if provider == "ollama":
            return OllamaJudge(ollama_host, ollama_model)
        
        return HeuristicJudge()