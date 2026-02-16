import json
import httpx
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict, field
import sys
import statistics
import logging
import traceback
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from config import EvaluatorConfig
from http_client import ChatbotClient
from scoring import ScoringStrategyFactory, ScoringStrategy, determine_winner


WINNER_DOTNET = "dotnet"
WINNER_PYTHON = "python"
WINNER_TIE = "tie"
WINNER_ERROR = "error"


@dataclass
class RunDetail:
    """Single judge run result."""
    run_index: int
    dotnet_score: float
    python_score: float
    winner: str
    comment: str


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
    judge_runs: int = 1
    dotnet_score_std: float = 0.0
    python_score_std: float = 0.0
    agreement_pct: float = 100.0
    run_details: List[RunDetail] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class JudgeEvaluator:
    PROMPTS_FILE = "quality-prompts.json"
    PROMPTS_KEY = "hr_evaluation_prompts"
    LOG_DIR = Path(__file__).parent.parent / "logs"
    
    def __init__(self, config: EvaluatorConfig):
        self.config = config
        self.dotnet_client = ChatbotClient(config.dotnet_url, config.api_timeout)
        self.python_client = ChatbotClient(config.python_url, config.api_timeout)
        self.scoring_strategy = self._create_scoring_strategy()
        self.prompts = self._load_prompts()
        self._setup_logging()
    
    def _create_scoring_strategy(self) -> ScoringStrategy:
        return ScoringStrategyFactory.create(
            provider=self.config.judge_provider,
            temperature=self.config.temperature,
            tie_tolerance=self.config.tie_tolerance,
            heuristic_tie_tolerance=self.config.heuristic_tie_tolerance,
            openai_timeout=self.config.openai_timeout,
            ollama_timeout=self.config.ollama_timeout,
            openai_api_key=self.config.openai_api_key,
            openai_model=self.config.openai_model,
            ollama_host=self.config.ollama_host,
            ollama_model=self.config.ollama_model
        )
    
    def _setup_logging(self) -> None:
        """Setup logging infrastructure for error tracking."""
        self.LOG_DIR.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.LOG_DIR / f"evaluation_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Evaluation started - Log file: {log_file}")
    
    def _load_prompts(self) -> List[Dict[str, Any]]:
        prompts_path = Path(__file__).parent.parent / self.PROMPTS_FILE
        
        with open(prompts_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        return data[self.PROMPTS_KEY]
    
    async def evaluate_all(self) -> List[EvaluationResult]:
        """Evaluate all prompts across both implementations."""
        results = []
        
        async with httpx.AsyncClient(timeout=self.config.api_timeout) as client:
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
        """Evaluate a single prompt with multiple judge runs."""
        question = prompt["question"]
        expected_criteria = prompt.get("expected_criteria", [])
        
        # Fetch API responses once
        dotnet_response = await self.dotnet_client.ask_question(client, question)
        python_response = await self.python_client.ask_question(client, question)
        
        # Run judge evaluation N times
        run_details = []
        failed_runs = 0
        
        for run_idx in range(self.config.judge_runs):
            try:
                evaluation = await self.scoring_strategy.evaluate(
                    question=question,
                    dotnet_response=dotnet_response,
                    python_response=python_response,
                    expected_criteria=expected_criteria
                )
                
                # Coerce scores to float safely
                dotnet_score = float(evaluation["dotnet_score"])
                python_score = float(evaluation["python_score"])
                
                # Derive winner from scores (ignore LLM self-reported winner)
                winner = determine_winner(dotnet_score, python_score, self.config.tie_tolerance)
                
                run_details.append(RunDetail(
                    run_index=run_idx + 1,
                    dotnet_score=dotnet_score,
                    python_score=python_score,
                    winner=winner,
                    comment=evaluation.get("comment", "")
                ))
                
                if self.config.judge_runs > 1:
                    print(f"  Run {run_idx + 1}/{self.config.judge_runs}: {winner}")
                    
            except Exception as e:
                failed_runs += 1
                error_msg = f"Run {run_idx + 1}/{self.config.judge_runs} failed for prompt '{prompt['id']}': {str(e)}"
                
                # Log full traceback to file
                self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
                
                # Print concise warning to console
                print(f"⚠️  {error_msg}")
                
                # Continue with remaining runs instead of crashing
                continue
        
        # Check if all runs failed
        if not run_details:
            error_msg = f"All {self.config.judge_runs} judge runs failed for prompt '{prompt['id']}'"
            self.logger.error(error_msg)
            print(f"❌ {error_msg}")
            
            # Return controlled error result instead of crashing
            return EvaluationResult(
                prompt_id=prompt["id"],
                question=question,
                dotnet_response=dotnet_response,
                python_response=python_response,
                dotnet_score=0.0,
                python_score=0.0,
                winner=WINNER_ERROR,
                judge_comment=f"Evaluation failed: All {self.config.judge_runs} runs encountered errors. Check logs for details.",
                judge_runs=self.config.judge_runs,
                dotnet_score_std=0.0,
                python_score_std=0.0,
                agreement_pct=0.0,
                run_details=[]
            )
        
        # Check if we have minimum required successful runs
        if len(run_details) < self.config.min_successful_runs:
            error_msg = (
                f"Prompt '{prompt['id']}': Only {len(run_details)}/{self.config.judge_runs} runs succeeded, "
                f"but min_successful_runs={self.config.min_successful_runs}"
            )
            self.logger.error(error_msg)
            print(f"❌ {error_msg}")
            
            return EvaluationResult(
                prompt_id=prompt["id"],
                question=question,
                dotnet_response=dotnet_response,
                python_response=python_response,
                dotnet_score=0.0,
                python_score=0.0,
                winner=WINNER_ERROR,
                judge_comment=f"Insufficient successful runs: {len(run_details)}/{self.config.judge_runs} (minimum: {self.config.min_successful_runs})",
                judge_runs=len(run_details),
                dotnet_score_std=0.0,
                python_score_std=0.0,
                agreement_pct=0.0,
                run_details=run_details
            )
        
        if failed_runs > 0:
            self.logger.warning(f"Prompt '{prompt['id']}': {failed_runs}/{self.config.judge_runs} runs failed")
        
        aggregated = self._aggregate_runs(run_details, self.config.tie_tolerance)
        
        return EvaluationResult(
            prompt_id=prompt["id"],
            question=question,
            dotnet_response=dotnet_response,
            python_response=python_response,
            dotnet_score=aggregated["mean_dotnet"],
            python_score=aggregated["mean_python"],
            winner=aggregated["final_winner"],
            judge_comment=run_details[0].comment if run_details else "",
            judge_runs=len(run_details),  # Actual successful runs
            dotnet_score_std=aggregated["std_dotnet"],
            python_score_std=aggregated["std_python"],
            agreement_pct=aggregated["agreement_pct"],
            run_details=run_details
        )
    
    def _aggregate_runs(self, run_details: List[RunDetail], tie_tolerance: float) -> Dict[str, Any]:
        if not run_details:
            return {
                "mean_dotnet": 0.0,
                "mean_python": 0.0,
                "std_dotnet": 0.0,
                "std_python": 0.0,
                "agreement_pct": 0.0,
                "final_winner": WINNER_TIE
            }
        
        dotnet_scores = [r.dotnet_score for r in run_details]
        python_scores = [r.python_score for r in run_details]
        
        mean_dotnet = statistics.mean(dotnet_scores)
        mean_python = statistics.mean(python_scores)
        
        # Standard deviation (0 if only one run)
        std_dotnet = statistics.stdev(dotnet_scores) if len(dotnet_scores) > 1 else 0.0
        std_python = statistics.stdev(python_scores) if len(python_scores) > 1 else 0.0
        
        # Agreement: percentage of runs agreeing with majority winner
        from collections import Counter
        winner_counts = Counter(r.winner for r in run_details)
        majority_winner = winner_counts.most_common(1)[0][0]
        agreement_count = winner_counts[majority_winner]
        agreement_pct = (agreement_count / len(run_details)) * 100
        
        final_winner = determine_winner(mean_dotnet, mean_python, tolerance=tie_tolerance)
        
        return {
            "mean_dotnet": round(mean_dotnet, 2),
            "mean_python": round(mean_python, 2),
            "std_dotnet": round(std_dotnet, 2),
            "std_python": round(std_python, 2),
            "agreement_pct": round(agreement_pct, 1),
            "final_winner": final_winner
        }
    
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
        dotnet_wins = sum(1 for r in results if r.winner == WINNER_DOTNET)
        python_wins = sum(1 for r in results if r.winner == WINNER_PYTHON)
        ties = sum(1 for r in results if r.winner == WINNER_TIE)
        
        avg_dotnet = sum(r.dotnet_score for r in results) / total
        avg_python = sum(r.python_score for r in results) / total
        
        judge_runs = results[0].judge_runs if results else 1
        avg_agreement = sum(r.agreement_pct for r in results) / total if results else 100.0
        
        summary = f"""## Summary
- Total prompts evaluated: {total}
- Judge runs per prompt: {judge_runs}
- .NET wins: {dotnet_wins} ({dotnet_wins/total*100:.1f}%)
- Python wins: {python_wins} ({python_wins/total*100:.1f}%)
- Ties: {ties} ({ties/total*100:.1f}%)

## Average Scores
- .NET: {avg_dotnet:.2f}/10
- Python: {avg_python:.2f}/10"""
        
        if judge_runs > 1:
            summary += f"\n\n## Multi-Run Statistics\n- Average agreement: {avg_agreement:.1f}%"
        
        return summary
    
    def _generate_detailed_results(self, results: List[EvaluationResult]) -> str:
        sections = []
        
        for result in results:
            scores_section = f"""- .NET: {result.dotnet_score}/10
- Python: {result.python_score}/10
- **Winner:** {result.winner.upper()}"""
            
            if result.judge_runs > 1:
                scores_section += f"""\n- .NET std dev: ±{result.dotnet_score_std:.2f}
- Python std dev: ±{result.python_score_std:.2f}
- Agreement: {result.agreement_pct:.1f}%"""
            
            section = f"""
### {result.prompt_id}
**Question:** {result.question}

**Scores:**
{scores_section}

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
