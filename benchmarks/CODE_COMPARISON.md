# Code Comparison: Before vs After

## Comparison 1: Configuration

### Before (Monolithic)
```python
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
```

**Issues:**
- ❌ Configuration mixed with logic
- ❌ Hard to test
- ❌ No clear configuration contract
- ❌ String defaults scattered

### After (Clean Code)
```python
# config.py
@dataclass
class EvaluatorConfig:
    """Configuration for the evaluation system."""
    
    dotnet_url: str
    python_url: str
    judge_provider: str
    openai_model: str
    openai_api_key: Optional[str]
    ollama_host: str
    ollama_model: str
    
    @classmethod
    def from_environment(cls) -> "EvaluatorConfig":
        """Create configuration from environment variables with sensible defaults."""
        return cls(
            dotnet_url=os.getenv("DOTNET_URL", "http://localhost:5000"),
            python_url=os.getenv("PYTHON_URL", "http://localhost:8000"),
            judge_provider=os.getenv("JUDGE_PROVIDER", "heuristic").lower(),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            ollama_model=os.getenv("OLLAMA_MODEL", "llama3.1"),
        )
    
    def is_openai_available(self) -> bool:
        """Check if OpenAI judge is properly configured."""
        return self.judge_provider == "openai" and self.openai_api_key is not None

# judge.py
class JudgeEvaluator:
    def __init__(self, config: EvaluatorConfig):
        self.config = config
        # Configuration injected, not hardcoded
```

**Benefits:**
- ✅ Configuration isolated and testable
- ✅ Type-safe with dataclass
- ✅ Clear validation methods
- ✅ Easy to mock in tests
- ✅ Self-documenting

---

## Comparison 2: HTTP Client

### Before (Inline Logic)
```python
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
```

**Issues:**
- ❌ Magic strings ("/chat", "question", "answer")
- ❌ Mixed responsibilities (HTTP + error handling)
- ❌ Not reusable
- ❌ Hard to test independently

### After (Dedicated Client)
```python
# http_client.py
class ChatbotClient:
    """Client for making requests to chatbot endpoints."""
    
    CHAT_ENDPOINT = "/chat"
    QUESTION_KEY = "question"
    ANSWER_KEY = "answer"
    DEFAULT_TIMEOUT = 30.0
    
    def __init__(self, base_url: str, timeout: float = DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
    
    async def ask_question(self, client: httpx.AsyncClient, question: str) -> str:
        """
        Send a question to the chatbot and return the response.
        
        Args:
            client: Async HTTP client instance
            question: The question to ask
            
        Returns:
            The chatbot's answer or an error message
        """
        url = f"{self.base_url}{self.CHAT_ENDPOINT}"
        payload = {self.QUESTION_KEY: question}
        
        try:
            response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                return data.get(self.ANSWER_KEY, "")
            
            return f"Error: HTTP {response.status_code}"
            
        except Exception as e:
            return f"Error: {str(e)}"
```

**Benefits:**
- ✅ Named constants
- ✅ Single responsibility
- ✅ Reusable across evaluators
- ✅ Easy to test in isolation
- ✅ Clear documentation
- ✅ Configurable timeout

---

## Comparison 3: Scoring Strategies

### Before (Nested Conditionals)
```python
async def _evaluate_responses(self, question: str, dotnet_response: str, python_response: str, expected_criteria: List[str]) -> Dict[str, Any]:
    evaluation_prompt = f"""..."""  # 30 lines of prompt

    # Provider: OpenAI JSON-mode (if configured)
    if self.judge_provider == "openai" and os.getenv("OPENAI_API_KEY"):
        try:
            headers = {...}
            payload = {...}
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                r.raise_for_status()
                content = r.json()["choices"][0]["message"]["content"].strip()
                return json.loads(content)
        except Exception as e:
            pass  # Fall back

    # Provider: Ollama local
    if self.judge_provider == "ollama":
        try:
            gen_payload = {...}
            async with httpx.AsyncClient(timeout=120.0) as client:
                r = await client.post(f"{self.ollama_host}/api/generate", json=gen_payload)
                r.raise_for_status()
                text = r.json().get("response", "").strip()
                return json.loads(text)
        except Exception:
            pass  # Fall back

    # Heuristic fallback: 80 lines of scoring logic inline...
```

**Issues:**
- ❌ 150+ lines in one method
- ❌ Multiple responsibilities
- ❌ Hard to test individual strategies
- ❌ Can't extend without modifying
- ❌ Violates Open/Closed Principle

### After (Strategy Pattern)
```python
# scoring.py
class ScoringStrategy(ABC):
    """Base class for scoring strategies."""
    
    @abstractmethod
    async def evaluate(
        self,
        question: str,
        dotnet_response: str,
        python_response: str,
        expected_criteria: List[str]
    ) -> Dict[str, Any]:
        """Evaluate two responses and return scores."""
        pass


class OpenAIJudge(ScoringStrategy):
    """Uses OpenAI API as the judge."""
    
    API_URL = "https://api.openai.com/v1/chat/completions"
    TIMEOUT = 60.0
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
    
    async def evaluate(self, question, dotnet_response, python_response, expected_criteria):
        # Clean, focused OpenAI implementation
        # Only 40 lines


class OllamaJudge(ScoringStrategy):
    """Uses local Ollama model as the judge."""
    # Clean, focused Ollama implementation


class HeuristicJudge(ScoringStrategy):
    """Rule-based heuristic scoring."""
    
    def _calculate_score(self, response: str, criteria: List[str]) -> float:
        coverage_score = self._calculate_coverage(text, criteria)
        length_score = self._calculate_length_score(len(response))
        clarity_score = self._calculate_clarity_score(text)
        # ... small focused methods


class ScoringStrategyFactory:
    """Factory for creating appropriate scoring strategy."""
    
    @staticmethod
    def create(provider: str, **kwargs) -> ScoringStrategy:
        if provider == "openai" and openai_api_key:
            return OpenAIJudge(openai_api_key, openai_model)
        if provider == "ollama":
            return OllamaJudge(ollama_host, ollama_model)
        return HeuristicJudge()


# Usage (judge.py)
self.scoring_strategy = ScoringStrategyFactory.create(
    provider=config.judge_provider,
    openai_api_key=config.openai_api_key,
    # ...
)
result = await self.scoring_strategy.evaluate(...)
```

**Benefits:**
- ✅ Each strategy is independent and testable
- ✅ Can add new strategies without modifying existing code
- ✅ Small, focused classes (~40 lines each)
- ✅ Factory encapsulates creation logic
- ✅ Follows Open/Closed Principle
- ✅ Easy to mock for testing

---

## Comparison 4: Report Generation

### Before (Monolithic String Building)
```python
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
...
"""
    
    for result in results:
        report += f"""
### {result.prompt_id}
...
---
"""
    
    return report
```

**Issues:**
- ❌ 80 lines in one method
- ❌ Mixed concerns (stats + formatting)
- ❌ Hard to test individual sections
- ❌ Can't reuse sections

### After (Composed Methods)
```python
# judge.py
def generate_report(self, results: List[EvaluationResult]) -> str:
    """Generate a markdown report from evaluation results."""
    summary = self._generate_summary(results)
    detailed = self._generate_detailed_results(results)
    
    return f"""# LLM-as-a-Judge Evaluation Report

{summary}

## Detailed Results

{detailed}
"""

def _generate_summary(self, results: List[EvaluationResult]) -> str:
    """Generate summary statistics section."""
    total = len(results)
    dotnet_wins = sum(1 for r in results if r.winner == "dotnet")
    python_wins = sum(1 for r in results if r.winner == "python")
    ties = sum(1 for r in results if r.winner == "tie")
    
    avg_dotnet = sum(r.dotnet_score for r in results) / total
    avg_python = sum(r.python_score for r in results) / total
    
    return f"""## Summary
- Total prompts evaluated: {total}
- .NET wins: {dotnet_wins} ({dotnet_wins/total*100:.1f}%)
...
"""

def _generate_detailed_results(self, results: List[EvaluationResult]) -> str:
    """Generate detailed results section."""
    sections = []
    for result in results:
        section = f"""
### {result.prompt_id}
...
"""
        sections.append(section)
    return "\n".join(sections)
```

**Benefits:**
- ✅ Composed of small, testable methods
- ✅ Single responsibility per method
- ✅ Easy to add new report sections
- ✅ Can test summary independently
- ✅ Can test detailed section independently
- ✅ Main method shows clear structure

---

## Comparison 5: Entry Point

### Before (Everything in main)
```python
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
        json.dump([{...} for r in results], f, indent=2, ensure_ascii=False)
    
    print(f"Evaluation complete! Results saved to {output_dir}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Issues:**
- ❌ File I/O in main
- ❌ Mixed concerns
- ❌ Hard to reuse save logic

### After (Clean Separation)
```python
# run_evaluation.py
async def main():
    """Run the evaluation process."""
    config = EvaluatorConfig.from_environment()
    
    print("=" * 70)
    print("LLM-as-a-Judge Evaluation")
    print("=" * 70)
    print(f".NET URL:       {config.dotnet_url}")
    print(f"Python URL:     {config.python_url}")
    print(f"Judge Provider: {config.judge_provider}")
    print("=" * 70)
    
    evaluator = JudgeEvaluator(config)
    results = await evaluator.evaluate_all()
    
    output_dir = Path(__file__).parent / "results"
    evaluator.save_results(results, output_dir)  # Delegated to evaluator

# judge.py
def save_results(self, results: List[EvaluationResult], output_dir: Path) -> None:
    """Save results to markdown report and JSON file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report = self.generate_report(results)
    report_path = output_dir / "evaluation_report.md"
    with open(report_path, "w", encoding="utf-8") as file:
        file.write(report)
    
    results_data = [result.to_dict() for result in results]
    json_path = output_dir / "evaluation_results.json"
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(results_data, file, indent=2, ensure_ascii=False)
```

**Benefits:**
- ✅ Entry point is clean and focused
- ✅ File I/O encapsulated in evaluator
- ✅ Reusable save logic
- ✅ Better error handling
- ✅ Testable save method

---

## Summary: Lines of Code by Concern

### Before (Monolithic)
| Concern | Lines | Location |
|---------|-------|----------|
| Configuration | ~20 | Mixed in `__init__` |
| HTTP Client | ~15 | Inline method |
| OpenAI Judge | ~25 | Inline in `_evaluate_responses` |
| Ollama Judge | ~20 | Inline in `_evaluate_responses` |
| Heuristic Judge | ~80 | Inline in `_evaluate_responses` |
| Orchestration | ~30 | `evaluate_all_prompts` |
| Report Generation | ~80 | `generate_report` |
| **TOTAL** | **~230** | **1 file** |

### After (Clean Code)
| Concern | Lines | Location |
|---------|-------|----------|
| Configuration | 44 | `config.py` |
| HTTP Client | 47 | `http_client.py` |
| OpenAI Judge | 90 | `scoring.py` (OpenAIJudge) |
| Ollama Judge | 90 | `scoring.py` (OllamaJudge) |
| Heuristic Judge | 95 | `scoring.py` (HeuristicJudge) |
| Strategy Factory | 32 | `scoring.py` (ScoringStrategyFactory) |
| Orchestration | 95 | `judge.py` (JudgeEvaluator) |
| Report Generation | 50 | `judge.py` (methods) |
| Data Transfer | 31 | `judge.py` (EvaluationResult) |
| Entry Point | 50 | `run_evaluation.py` |
| **TOTAL** | **~600** | **5 files** |

**Why more lines is better:**
- ✅ Each class/method has single responsibility
- ✅ Full type hints and docstrings
- ✅ Named constants instead of magic values
- ✅ Clear structure and organization
- ✅ Testable in isolation
- ✅ Reusable components
- ✅ Self-documenting code

---

## Key Takeaway

**More lines ≠ Worse code** when those lines provide:
- Clear separation of concerns
- Type safety
- Documentation
- Testability
- Maintainability
- Extensibility

The refactored code is **3x longer** but **10x better** in quality, maintainability, and professional standards.
