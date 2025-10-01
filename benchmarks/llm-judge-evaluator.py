#!/usr/bin/env python3
"""
LLM-as-a-Judge evaluator for comparing .NET vs Python chatbot responses
"""

import json
import asyncio
import aiohttp
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
        self.dotnet_url = dotnet_url
        self.python_url = python_url
        self.evaluation_prompts = self._load_prompts()
    
    def _load_prompts(self) -> List[Dict[str, Any]]:
        prompts_file = Path(__file__).parent / "quality-prompts.json"
        with open(prompts_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data["hr_evaluation_prompts"]
    
    async def _make_request(self, session: aiohttp.ClientSession, url: str, question: str) -> str:
        payload = {"question": question}
        try:
            async with session.post(f"{url}/chat", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("answer", "")
                else:
                    return f"Error: {response.status}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _evaluate_responses(self, question: str, dotnet_response: str, python_response: str) -> Dict[str, Any]:
        
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
        
        return {
            "dotnet_score": 8.0,
            "python_score": 7.5,
            "winner": "dotnet",
            "comment": "Mock evaluation - implement with actual LLM"
        }
    
    async def evaluate_all_prompts(self) -> List[EvaluationResult]:
        results = []
        
        async with aiohttp.ClientSession() as session:
            for prompt in self.evaluation_prompts:
                question = prompt["question"]
                
                dotnet_response = await self._make_request(session, self.dotnet_url, question)
                python_response = await self._make_request(session, self.python_url, question)
                
                evaluation = await self._evaluate_responses(question, dotnet_response, python_response)
                
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
