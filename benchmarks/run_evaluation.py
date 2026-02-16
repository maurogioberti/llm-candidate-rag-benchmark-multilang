#!/usr/bin/env python3
"""
LLM Judge Evaluator Entry Point

Configuration:
    config/common.yaml      - System topology (API URLs, LLM connections)
    config/evaluation.yaml  - Methodology (judge runs, temperature, tolerance)
    ENV variables           - Override layer (JUDGE_PROVIDER, JUDGE_RUNS, etc.)

Precedence: ENV > evaluation.yaml > common.yaml > defaults
"""

import asyncio
from pathlib import Path

from evaluator.judge import JudgeEvaluator
from evaluator.config import EvaluatorConfig


SEPARATOR_WIDTH = 70


def _load_config() -> EvaluatorConfig:
    try:
        return EvaluatorConfig.from_yaml()
    except FileNotFoundError:
        print("⚠️  config/common.yaml not found, using environment variables only")
        return EvaluatorConfig.from_environment()


def _print_header(config: EvaluatorConfig) -> None:
    print("=" * SEPARATOR_WIDTH)
    print("LLM-as-a-Judge Evaluation")
    print("=" * SEPARATOR_WIDTH)
    print(f".NET URL:       {config.dotnet_url}")
    print(f"Python URL:     {config.python_url}")
    print(f"Judge Provider: {config.judge_provider}")
    print(f"Judge Runs:     {config.judge_runs}")
    print(f"Temperature:    {config.temperature}")
    _print_provider_info(config)
    print("=" * SEPARATOR_WIDTH)
    print("\nStarting evaluation...\n")


def _print_provider_info(config: EvaluatorConfig) -> None:
    if config.is_openai_available():
        print(f"OpenAI Model:   {config.openai_model}")
    elif config.is_ollama_enabled():
        print(f"Ollama Host:    {config.ollama_host}")
        print(f"Ollama Model:   {config.ollama_model}")


def _print_footer() -> None:
    print("\n" + "=" * SEPARATOR_WIDTH)
    print("Evaluation complete!")
    print("=" * SEPARATOR_WIDTH)


async def main():
    config = _load_config()
    
    try:
        config.validate()
    except ValueError as e:
        print(f"\n❌ Configuration Error:\n{e}\n")
        return
    
    _print_header(config)
    
    evaluator = JudgeEvaluator(config)
    results = await evaluator.evaluate_all()
    
    output_dir = Path(__file__).parent / "results"
    evaluator.save_results(results, output_dir)
    
    _print_footer()


if __name__ == "__main__":
    asyncio.run(main())
