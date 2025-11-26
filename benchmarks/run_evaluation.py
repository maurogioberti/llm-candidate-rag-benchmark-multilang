#!/usr/bin/env python3
"""
Entry point for running the LLM Judge Evaluator.

Usage:
    python run_evaluation.py

Environment Variables:
    DOTNET_URL       - .NET API endpoint (default: http://localhost:5000)
    PYTHON_URL       - Python API endpoint (default: http://localhost:8000)
    JUDGE_PROVIDER   - Judge type: heuristic|openai|ollama (default: heuristic)
    OPENAI_API_KEY   - OpenAI API key (required if JUDGE_PROVIDER=openai)
    OPENAI_MODEL     - OpenAI model (default: gpt-4o-mini)
    OLLAMA_HOST      - Ollama host URL (default: http://localhost:11434)
    OLLAMA_MODEL     - Ollama model (default: llama3.1)
"""

import asyncio
from pathlib import Path

from evaluator.judge import JudgeEvaluator
from evaluator.config import EvaluatorConfig


async def main():
    config = EvaluatorConfig.from_environment()
    
    print("=" * 70)
    print("LLM-as-a-Judge Evaluation")
    print("=" * 70)
    print(f".NET URL:       {config.dotnet_url}")
    print(f"Python URL:     {config.python_url}")
    print(f"Judge Provider: {config.judge_provider}")
    
    if config.is_openai_available():
        print(f"OpenAI Model:   {config.openai_model}")
    elif config.is_ollama_enabled():
        print(f"Ollama Host:    {config.ollama_host}")
        print(f"Ollama Model:   {config.ollama_model}")
    
    print("=" * 70)
    print("\nStarting evaluation...\n")
    
    evaluator = JudgeEvaluator(config)
    results = await evaluator.evaluate_all()
    
    output_dir = Path(__file__).parent / "results"
    evaluator.save_results(results, output_dir)
    
    print("\n" + "=" * 70)
    print("Evaluation complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
