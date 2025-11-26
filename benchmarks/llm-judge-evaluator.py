#!/usr/bin/env python3
"""
LLM-as-a-Judge evaluator for comparing .NET vs Python chatbot responses.

Features:
- Fetches answers from two endpoints (.NET and Python) for each prompt
- Judges with one of:
    - OpenAI (if JUDGE_PROVIDER=openai and OPENAI_API_KEY set)
    - Ollama local model (if JUDGE_PROVIDER=ollama)
    - Heuristic fallback (no external LLM required)
- Saves a Markdown report and JSON results under benchmarks/results/

Env overrides (optional):
- DOTNET_URL (default http://localhost:5000)
- PYTHON_URL (default http://localhost:8000)
- JUDGE_PROVIDER (heuristic | openai | ollama; default heuristic)
- OPENAI_MODEL (default gpt-4o-mini)
- OLLAMA_HOST (default http://localhost:11434)
- OLLAMA_MODEL (default llama3.1)
"""

import json
import os
import asyncio
import httpx
from typing import Dict, List, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class EvaluationResult:
    prompt_id: str
    question: str
    dotnet_response: str
    python_response: str
    dotnet_score: float
    python_score: float
    winner: str
    judge_comment: str

class LLMJudgeEvaluator:
    def __init__(self, dotnet_url: str = "http://localhost:5000", python_url: str = "http://localhost:8000"):
        # Allow env overrides for endpoints
        self.dotnet_url = os.getenv("DOTNET_URL", dotnet_url)
        self.python_url = os.getenv("PYTHON_URL", python_url)

        # Provider selection: heuristic | openai | ollama
        self.judge_provider = os.getenv("JUDGE_PROVIDER", "heuristic").lower()
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1")

        self.evaluation_prompts = self._load_prompts()
    
    def _load_prompts(self) -> List[Dict[str, Any]]:
        prompts_file = Path(__file__).parent / "quality-prompts.json"
        with open(prompts_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data["hr_evaluation_prompts"]
    
    async def _make_request(self, client: httpx.AsyncClient, url: str, question: str) -> str:
        payload = {"question": question}
        try:
            resp = await client.post(f"{url}/chat", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("answer", "")
            return f"Error: HTTP {resp.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _evaluate_responses(self, question: str, dotnet_response: str, python_response: str, expected_criteria: List[str]) -> Dict[str, Any]:

        evaluation_prompt = f"""
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

        # Provider: OpenAI JSON-mode (if configured)
        if self.judge_provider == "openai" and os.getenv("OPENAI_API_KEY"):
            try:
                headers = {
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": self.openai_model,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": "You are a strict evaluator. Respond ONLY valid JSON matching the schema."},
                        {"role": "user", "content": evaluation_prompt},
                    ],
                }
                async with httpx.AsyncClient(timeout=60.0) as client:
                    r = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                    r.raise_for_status()
                    content = r.json()["choices"][0]["message"]["content"].strip()
                    return json.loads(content)
            except Exception as e:
                # Fall back to heuristic if OpenAI fails
                pass

        # Provider: Ollama local
        if self.judge_provider == "ollama":
            try:
                gen_payload = {
                    "model": self.ollama_model,
                    "prompt": evaluation_prompt + "\n\nRespond ONLY with a valid JSON object.",
                    "stream": False,
                }
                async with httpx.AsyncClient(timeout=120.0) as client:
                    r = await client.post(f"{self.ollama_host}/api/generate", json=gen_payload)
                    r.raise_for_status()
                    text = r.json().get("response", "").strip()
                    return json.loads(text)
            except Exception:
                # Fall back to heuristic if Ollama fails
                pass

        # Heuristic fallback: rule-based scoring, no external LLM required
        def score_text(txt: str, criteria: List[str]) -> float:
            if not txt or txt.lower().startswith("error:"):
                return 1.0
            text = txt.lower()

            # Accuracy/Completeness via keyword coverage
            crit = [c.lower() for c in criteria] if criteria else []
            coverage = 0.0
            if crit:
                hits = sum(1 for c in crit if c in text)
                coverage = hits / max(1, len(crit))  # 0..1

            # Length proxy for completeness/detail
            ln = len(txt)
            length_score = 0.0
            if ln > 800:
                length_score = 1.0
            elif ln > 300:
                length_score = 0.7
            elif ln > 120:
                length_score = 0.4
            else:
                length_score = 0.1

            # Clarity: lists / paragraphs
            clarity = 0.0
            if any(b in text for b in ["\n- ", "\n* ", "1.", "2.", "3."]):
                clarity = 0.8
            elif "\n\n" in text:
                clarity = 0.5
            else:
                clarity = 0.2

            # Actionability cues
            actionability = 1.0 if any(k in text for k in ["recommend", "next step", "should", "interview", "hire"]) else 0.2

            # Ranking cues
            ranking = 1.0 if any(k in text for k in ["rank", "ranking", "top", "1.", "2.", "3."]) else 0.2

            # Map subscores to 0..10 roughly balancing criteria
            # weights chosen to keep max near 10
            raw = (
                3.5 * coverage + 2.5 * length_score + 1.5 * clarity + 1.25 * actionability + 1.25 * ranking
            )
            return max(0.0, min(10.0, raw))

        ds = score_text(dotnet_response, expected_criteria)
        ps = score_text(python_response, expected_criteria)

        # Winner with small tolerance
        tol = 0.25
        if abs(ds - ps) <= tol:
            winner = "tie"
        else:
            winner = "dotnet" if ds > ps else "python"

        return {
            "dotnet_score": round(ds, 2),
            "python_score": round(ps, 2),
            "winner": winner,
            "comment": "Heuristic baseline judge used (no external LLM). Set JUDGE_PROVIDER=openai or ollama to use an LLM-as-a-judge.",
        }
    
    async def evaluate_all_prompts(self) -> List[EvaluationResult]:
        results = []

        # Shared async HTTP client with timeout
        async with httpx.AsyncClient(timeout=30.0) as client:
            for prompt in self.evaluation_prompts:
                question = prompt["question"]
                expected_criteria = prompt.get("expected_criteria", [])

                dotnet_response = await self._make_request(client, self.dotnet_url, question)
                python_response = await self._make_request(client, self.python_url, question)

                evaluation = await self._evaluate_responses(question, dotnet_response, python_response, expected_criteria)

                result = EvaluationResult(
                    prompt_id=prompt["id"],
                    question=question,
                    dotnet_response=dotnet_response,
                    python_response=python_response,
                    dotnet_score=evaluation["dotnet_score"],
                    python_score=evaluation["python_score"],
                    winner=evaluation["winner"],
                    judge_comment=evaluation["comment"]
                )
                
                results.append(result)
                print(f"Evaluated: {prompt['id']} - Winner: {evaluation['winner']}")
        
        return results
    
    def generate_report(self, results: List[EvaluationResult]) -> str:
        
        dotnet_wins = sum(1 for r in results if r.winner == "dotnet")
        python_wins = sum(1 for r in results if r.winner == "python")
        ties = sum(1 for r in results if r.winner == "tie")
        
        avg_dotnet_score = sum(r.dotnet_score for r in results) / len(results)
        avg_python_score = sum(r.python_score for r in results) / len(results)
        
        report = f"""
# LLM-as-a-Judge Evaluation Report

## Summary
- Total prompts evaluated: {len(results)}
- .NET wins: {dotnet_wins} ({dotnet_wins/len(results)*100:.1f}%)
- Python wins: {python_wins} ({python_wins/len(results)*100:.1f}%)
- Ties: {ties} ({ties/len(results)*100:.1f}%)

## Average Scores
- .NET: {avg_dotnet_score:.2f}/10
- Python: {avg_python_score:.2f}/10

## Detailed Results

"""
        
        for result in results:
            report += f"""
### {result.prompt_id}
**Question:** {result.question}

**Scores:**
- .NET: {result.dotnet_score}/10
- Python: {result.python_score}/10
- **Winner:** {result.winner.upper()}

**Judge Comment:** {result.judge_comment}

---
"""
        
        return report

async def main():
    evaluator = LLMJudgeEvaluator()
    
    print("Starting LLM-as-a-Judge evaluation...")
    print(f".NET URL: {evaluator.dotnet_url} | Python URL: {evaluator.python_url} | Provider: {evaluator.judge_provider}")
    results = await evaluator.evaluate_all_prompts()
    
    report = evaluator.generate_report(results)
    
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "evaluation_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    with open(output_dir / "evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump([{
            "prompt_id": r.prompt_id,
            "question": r.question,
            "dotnet_response": r.dotnet_response,
            "python_response": r.python_response,
            "dotnet_score": r.dotnet_score,
            "python_score": r.python_score,
            "winner": r.winner,
            "judge_comment": r.judge_comment
        } for r in results], f, indent=2, ensure_ascii=False)
    
    print(f"Evaluation complete! Results saved to {output_dir}")
    print(f"Report: {output_dir / 'evaluation_report.md'}")

if __name__ == "__main__":
    asyncio.run(main())
