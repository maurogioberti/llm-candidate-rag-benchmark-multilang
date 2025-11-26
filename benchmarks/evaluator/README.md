# LLM Judge Evaluator

A modular quality evaluation framework for comparing chatbot implementations using the LLM-as-a-Judge methodology.

## Overview

This tool evaluates and compares two chatbot implementations (.NET with Semantic Kernel and Python with LangChain) by:

1. Sending HR-related questions to both APIs
2. Scoring responses using configurable judge strategies
3. Generating comprehensive comparison reports

## Architecture

```
benchmarks/evaluator/
├── __init__.py          # Module exports
├── config.py            # Configuration management
├── http_client.py       # HTTP communication with chatbot APIs
├── judge.py             # Core evaluation orchestration
└── scoring.py           # Scoring strategies (OpenAI, Ollama, Heuristic)
```

### Design Principles

- **Single Responsibility**: Each module handles one concern
- **Strategy Pattern**: Pluggable scoring strategies (OpenAI, Ollama, Heuristic)
- **Dependency Injection**: Configuration and clients injected, not hardcoded
- **Clean Interfaces**: Protocol-based design with clear abstractions
- **Type Safety**: Full type hints for better IDE support and validation

## Quick Start

### Basic Usage

```bash
# From benchmarks/ directory
python run_evaluation.py
```

### With Environment Configuration

```bash
# Use OpenAI as judge
export JUDGE_PROVIDER=openai
export OPENAI_API_KEY=your_key_here
python run_evaluation.py

# Use Ollama local model as judge
export JUDGE_PROVIDER=ollama
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=llama3.1
python run_evaluation.py

# Heuristic fallback (no external LLM)
export JUDGE_PROVIDER=heuristic
python run_evaluation.py
```

## Configuration

All configuration is via environment variables with sensible defaults:

| Variable | Default | Description |
|----------|---------|-------------|
| `DOTNET_URL` | `http://localhost:5000` | .NET API endpoint |
| `PYTHON_URL` | `http://localhost:8000` | Python API endpoint |
| `JUDGE_PROVIDER` | `heuristic` | Judge type: `heuristic`, `openai`, or `ollama` |
| `OPENAI_API_KEY` | None | OpenAI API key (required for `openai` provider) |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama service URL |
| `OLLAMA_MODEL` | `llama3.1` | Ollama model to use |

## Scoring Strategies

### 1. OpenAI Judge (Recommended)

Uses OpenAI's GPT models for intelligent evaluation.

**Pros:**
- Most accurate and nuanced evaluation
- Understands context and intent
- Provides detailed reasoning

**Cons:**
- Requires API key and costs money
- External dependency

### 2. Ollama Judge

Uses local Ollama models for evaluation.

**Pros:**
- Free and private
- No external API calls
- Good for development/testing

**Cons:**
- Requires Ollama installation
- Quality depends on model size
- Slower than OpenAI

### 3. Heuristic Judge (Default)

Rule-based scoring without external LLM.

**Pros:**
- No external dependencies
- Fast and deterministic
- Always available

**Cons:**
- Less nuanced than LLM judges
- May miss context
- Baseline quality only

## Evaluation Criteria

Each response is evaluated on:

1. **Accuracy** - Correctness and relevance
2. **Completeness** - Coverage of expected criteria
3. **Clarity** - Easy to understand and well-structured
4. **Actionability** - Provides actionable HR insights
5. **Ranking Quality** - Logical ordering of candidates

### Scoring Scale

- **0-2**: Very poor - Does not answer the question
- **3-4**: Poor - Partial or incorrect response
- **5-6**: Acceptable - Basic but incomplete response
- **7-8**: Good - Complete and accurate response
- **9-10**: Excellent - Exceptional and detailed response

## Output

Results are saved to `benchmarks/results/`:

- `evaluation_report.md` - Human-readable markdown report
- `evaluation_results.json` - Machine-readable JSON data

### Report Sections

1. **Summary** - Win/loss/tie counts and percentages
2. **Average Scores** - Mean scores for each implementation
3. **Detailed Results** - Per-prompt breakdown with judge comments

## Programmatic Usage

```python
import asyncio
from pathlib import Path
from evaluator import JudgeEvaluator, EvaluatorConfig

async def custom_evaluation():
    # Create custom configuration
    config = EvaluatorConfig(
        dotnet_url="http://localhost:5000",
        python_url="http://localhost:8000",
        judge_provider="openai",
        openai_model="gpt-4",
        openai_api_key="your-key",
        ollama_host="http://localhost:11434",
        ollama_model="llama3.1"
    )
    
    # Run evaluation
    evaluator = JudgeEvaluator(config)
    results = await evaluator.evaluate_all()
    
    # Save results
    output_dir = Path("./results")
    evaluator.save_results(results, output_dir)
    
    return results

# Run
asyncio.run(custom_evaluation())
```

## Extending the Evaluator

### Add a New Scoring Strategy

```python
# In scoring.py
from .scoring import ScoringStrategy

class CustomJudge(ScoringStrategy):
    async def evaluate(self, question, dotnet_response, python_response, expected_criteria):
        # Your custom logic here
        return {
            "dotnet_score": 8.5,
            "python_score": 7.2,
            "winner": "dotnet",
            "comment": "Your reasoning"
        }

# Register in ScoringStrategyFactory
```

### Add New Evaluation Prompts

Edit `quality-prompts.json`:

```json
{
  "hr_evaluation_prompts": [
    {
      "id": "your-prompt-id",
      "question": "Your question here",
      "expected_criteria": ["criterion1", "criterion2"]
    }
  ]
}
```

## Troubleshooting

### APIs not responding

```bash
# Check if services are running
curl http://localhost:5000/health
curl http://localhost:8000/health
```

### OpenAI judge not working

- Verify `OPENAI_API_KEY` is set
- Check API key has sufficient credits
- Ensure network access to OpenAI API

### Ollama judge failing

```bash
# Check Ollama is running
curl http://localhost:11434/api/version

# Pull required model
ollama pull llama3.1
```

## Clean Code Improvements

This refactored version implements:

✅ **Separation of Concerns** - Each file has a single responsibility  
✅ **Strategy Pattern** - Pluggable scoring strategies  
✅ **Dependency Injection** - Configuration and dependencies injected  
✅ **Type Safety** - Full type hints throughout  
✅ **Clear Naming** - Descriptive class and method names  
✅ **No Magic Numbers** - Constants defined and named  
✅ **Minimal Comments** - Self-documenting code with docs where needed  
✅ **Error Handling** - Graceful degradation with fallbacks  
✅ **Testability** - Easy to mock and test each component  

## Integration with Repository

This evaluator follows the same patterns as the main application:

- **Config Management**: Similar to `core.infrastructure.shared.config_loader`
- **Client Pattern**: Similar to `HttpEmbeddingsClient`
- **Service Layer**: Similar to `CandidateService`
- **Use Cases**: Orchestration pattern like `AskQuestionUseCase`
- **DTOs**: Dataclasses for data transfer like `ChatResult`

---

**Location**: `benchmarks/evaluator/` - Lives with other benchmark tools where it belongs.
