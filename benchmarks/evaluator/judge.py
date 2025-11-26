import json
import httpx
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
import sys

sys.path.insert(0, str(Path(__file__).parent))

from config import EvaluatorConfig
from http_client import ChatbotClient
from scoring import ScoringStrategyFactory, ScoringStrategy


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
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class JudgeEvaluator:
    PROMPTS_FILE = "quality-prompts.json"
    PROMPTS_KEY = "hr_evaluation_prompts"
    
    def __init__(self, config: EvaluatorConfig):
        self.config = config
        self.dotnet_client = ChatbotClient(config.dotnet_url)
        self.python_client = ChatbotClient(config.python_url)
        self.scoring_strategy = self._create_scoring_strategy()
        self.prompts = self._load_prompts()
    
    def _create_scoring_strategy(self) -> ScoringStrategy:
        return ScoringStrategyFactory.create(
            provider=self.config.judge_provider,
            openai_api_key=self.config.openai_api_key,
            openai_model=self.config.openai_model,
            ollama_host=self.config.ollama_host,
            ollama_model=self.config.ollama_model
        )
    
    def _load_prompts(self) -> List[Dict[str, Any]]:
        prompts_path = Path(__file__).parent.parent / self.PROMPTS_FILE
        
        with open(prompts_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        return data[self.PROMPTS_KEY]
    
    async def evaluate_all(self) -> List[EvaluationResult]:
        """Evaluate all prompts across both implementations."""
        results = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for prompt in self.prompts:
                result = await self._evaluate_single_prompt(client, prompt)
                results.append(result)
                print(f"Evaluated: {prompt['id']} - Winner: {result.winner}")
        
        return results
    
    async def _evaluate_single_prompt(
        self,
        client: httpx.AsyncClient,
        prompt: Dict[str, Any]
    ) -> EvaluationResult:
        question = prompt["question"]
        expected_criteria = prompt.get("expected_criteria", [])
        
        dotnet_response = await self.dotnet_client.ask_question(client, question)
        python_response = await self.python_client.ask_question(client, question)
        
        evaluation = await self.scoring_strategy.evaluate(
            question=question,
            dotnet_response=dotnet_response,
            python_response=python_response,
            expected_criteria=expected_criteria
        )
        
        return EvaluationResult(
            prompt_id=prompt["id"],
            question=question,
            dotnet_response=dotnet_response,
            python_response=python_response,
            dotnet_score=evaluation["dotnet_score"],
            python_score=evaluation["python_score"],
            winner=evaluation["winner"],
            judge_comment=evaluation["comment"]
        )
    
    def generate_report(self, results: List[EvaluationResult]) -> str:
        """Generate markdown report from evaluation results."""
        summary = self._generate_summary(results)
        detailed = self._generate_detailed_results(results)
        
        return f"""# LLM-as-a-Judge Evaluation Report

{summary}

## Detailed Results

{detailed}
"""
    
    def _generate_summary(self, results: List[EvaluationResult]) -> str:
        total = len(results)
        dotnet_wins = sum(1 for r in results if r.winner == "dotnet")
        python_wins = sum(1 for r in results if r.winner == "python")
        ties = sum(1 for r in results if r.winner == "tie")
        
        avg_dotnet = sum(r.dotnet_score for r in results) / total
        avg_python = sum(r.python_score for r in results) / total
        
        return f"""## Summary
- Total prompts evaluated: {total}
- .NET wins: {dotnet_wins} ({dotnet_wins/total*100:.1f}%)
- Python wins: {python_wins} ({python_wins/total*100:.1f}%)
- Ties: {ties} ({ties/total*100:.1f}%)

## Average Scores
- .NET: {avg_dotnet:.2f}/10
- Python: {avg_python:.2f}/10"""
    
    def _generate_detailed_results(self, results: List[EvaluationResult]) -> str:
        sections = []
        
        for result in results:
            section = f"""
### {result.prompt_id}
**Question:** {result.question}

**Scores:**
- .NET: {result.dotnet_score}/10
- Python: {result.python_score}/10
- **Winner:** {result.winner.upper()}

**Judge Comment:** {result.judge_comment}

---"""
            sections.append(section)
        
        return "\n".join(sections)
    
    def save_results(
        self,
        results: List[EvaluationResult],
        output_dir: Path
    ) -> None:
        """Save evaluation results to markdown report and JSON file."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report = self.generate_report(results)
        report_path = output_dir / "evaluation_report.md"
        with open(report_path, "w", encoding="utf-8") as file:
            file.write(report)
        
        results_data = [result.to_dict() for result in results]
        json_path = output_dir / "evaluation_results.json"
        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(results_data, file, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to {output_dir}")
        print(f"Report: {report_path}")
        print(f"JSON: {json_path}")


async def main():
    try:
        config = EvaluatorConfig.from_yaml()
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Configuration Error: {e}")
        raise
    
    print("🚀 Starting LLM-as-a-Judge Evaluator")
    print(f"  .NET URL: {config.dotnet_url}")
    print(f"  Python URL: {config.python_url}")
    print(f"  Judge Provider: {config.judge_provider}")
    print(f"  Ollama Model: {config.ollama_model}")
    print()
    
    evaluator = JudgeEvaluator(config)
    results = await evaluator.evaluate_all()
    
    output_dir = Path(__file__).parent.parent / "results"
    evaluator.save_results(results, output_dir)
    
    print("\n✅ Evaluation complete!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
