# LLM Judge Evaluator

A modular, statistically robust quality evaluation framework for comparing chatbot implementations using the LLM-as-a-Judge methodology with multi-run support.

## Overview

This evaluator compares two chatbot implementations (.NET with Semantic Kernel and Python with LangChain) by:

1. Sending HR-related questions to both APIs
2. Running configurable multiple judge evaluations per prompt
3. Aggregating results statistically (mean, standard deviation, agreement)
4. Deriving winners from aggregated scores, not LLM self-reports
5. Generating comprehensive comparison reports with confidence metrics

## Architecture

```
benchmarks/evaluator/
├── config.py            # Configuration with multi-run support
├── http_client.py       # HTTP communication with chatbot APIs
├── judge.py             # Evaluation orchestration + aggregation
├── scoring.py           # Scoring strategies + winner determination
└── README.md            # This file
```

### Design Principles

- **Single Responsibility**: Each module handles one concern
- **Strategy Pattern**: Pluggable scoring strategies (OpenAI, Ollama, Heuristic)
- **Statistical Rigor**: Multi-run evaluation with aggregation
- **Fail-Fast**: Strategies raise exceptions; orchestrator handles failures
- **Type Safety**: Full type hints throughout

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

Configuration via `config/common.yaml` or environment variables (env vars override YAML):

| Variable | Default | Description |
|----------|---------|-------------|
| `DOTNET_URL` | `http://localhost:5000` | .NET API endpoint |
| `PYTHON_URL` | `http://localhost:8000` | Python API endpoint |
| `JUDGE_PROVIDER` | `ollama` | Judge type: `heuristic`, `openai`, or `ollama` |
| `JUDGE_RUNS` | `1` | **Number of judge evaluations per prompt (for statistical analysis)** |
| `OPENAI_API_KEY` | None | OpenAI API key (required for `openai` provider) |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama service URL |
| `OLLAMA_MODEL` | from YAML | Ollama model to use (e.g., `llama3:8b`) |

### Multi-Run Statistical Evaluation

Set `JUDGE_RUNS` to run the judge multiple times per prompt:

```bash
# Single run (default, backward compatible)
python run_evaluation.py

# 5 runs per prompt for statistical significance
export JUDGE_RUNS=5
python run_evaluation.py

# 10 runs for high-confidence metrics
export JUDGE_RUNS=10
python run_evaluation.py
```

**How it works:**
1. API responses fetched **once** per prompt (not per run)
2. Judge evaluates the same responses **N times** (configured by `JUDGE_RUNS`)
3. Scores aggregated: mean, standard deviation, agreement percentage
4. Winner derived from **mean scores**, not individual runs

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
- Baseline quality only with statistical metrics
- `evaluation_results.json` - Machine-readable JSON data with per-run details
- `benchmarks/logs/evaluation_YYYYMMDD_HHMMSS.log` - Detailed logs with error traces

### Report Sections

1. **Summary**
   - Win/loss/tie counts and percentages
   - Judge runs per prompt
   Error Handling & Robustness

### Graceful Failure Handling

- **Judge run failures**: Logged to file, run skipped, evaluation continues
- **Partial failures**: If some runs succeed, aggregation uses successful runs only
- **All runs fail**: Returns error result with `winner="error"` instead of crashing
- **API errors**: Captured in response string, judge evaluates the error message
- **Config errors**: Fail fast at startup with helpful messages

### Failure Logs

All failures are logged to `benchmarks/logs/` with:
- Full exception traces
- Timestamp
- Prompt ID and run number
- Concise console warnings during evaluation

## Programmatic Usage

```python
import asyncio
from pathlib import Path
from evaluator.judge import JudgeEvaluator
from evaluator.config import EvaluatorConfig

async def multi_run_evaluation():
    # Load from YAML with overrides
    config = EvaluatorConfig.from_yaml()
    config.judge_runs = 5  # Override for statistical robustness
    
    # Validate before running
    config.validate()
    
    # Run evaluation
    evaluator = JudgeEvaluator(config)
    results = await evaluator.evaluate_all()
    
    # Access aggregated statistics
    for result in results:
        print(f"{result.prompt_id}:")
        print(f"  Winner: {result.winner}")
        print(f"  .NET: {result.dotnet_score:.2f} (±{result.dotnet_score_std:.2f})")
        print(f"  Python: {result.python_score:.2f} (±{result.python_score_std:.2f})")
        print(f"  Agreement: {result.agreement_pct:.1f}%")
    
    # Save results
    output_dir = Path("./results")
    evaluator.save_results(results, output_dir)
    
    return results

asyncio.run(multi_run_evaluation())
```

## Architecture Details

### Winner Determination

Winners are **always** derived from scores using the `determine_winner()` function in `scoring.py`:

```python
def determine_winner(dotnet_score: float, python_score: float, tolerance: float = 0.01) -> str:
    """Determine winner from scores with configurable tie tolerance."""
    diff = abs(dotnet_score - python_score)
    if diff <= tolerance:
        return "tie"
    return "dotnet" if dotnet_score > python_score else "python"
```

**Why not trust LLM self-reported winner?**
- LLMs can contradict their own scores
- Score-derived winners are deterministic and auditable
- Consistent logic across all judge types (OpenAI, Ollama, Heuristic)

### Aggregation Logic

Located in `judge.py` as `_aggregate_runs()`:

1. Collect all successful run scores
2. Compute mean and standard deviation for both implementations
3. Determine majority winner (most frequent winner across runs)
4. Calculate agreement percentage (% agreeing with majority)
5. Derive final winner from mean scores (not from majority vote)

**Note**: Final winner comes from mean scores, not majority vote. This handles edge cases where majority winner disagrees with statistical mean.

### Sequential vs Parallel Execution

Current implementation: **sequential** (runs execute one after another)

Future consideration: Parallel execution with `asyncio.gather()` and configurable concurrency limiter for rate-limiting-sensitive providers.
