# Architecture Diagrams

## 1. Module Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    benchmarks/evaluator/                         │
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │   config.py  │────▶│   judge.py   │◀────│http_client.py│   │
│  │              │     │              │     │              │   │
│  │ Configuration│     │ Orchestrator │     │  HTTP Client │   │
│  └──────────────┘     └──────┬───────┘     └──────────────┘   │
│                              │                                  │
│                              ▼                                  │
│                       ┌──────────────┐                         │
│                       │  scoring.py  │                         │
│                       │              │                         │
│                       │  Strategies  │                         │
│                       └──────────────┘                         │
│                              │                                  │
│         ┌────────────────────┼────────────────────┐           │
│         ▼                    ▼                     ▼           │
│  ┌────────────┐      ┌────────────┐      ┌────────────┐      │
│  │  OpenAI    │      │   Ollama   │      │ Heuristic  │      │
│  │   Judge    │      │    Judge   │      │   Judge    │      │
│  └────────────┘      └────────────┘      └────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ imported by
                              ▼
                  ┌───────────────────────┐
                  │  run_evaluation.py    │
                  │                       │
                  │    Entry Point        │
                  └───────────────────────┘
```

## 2. Class Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Configuration Layer                       │
└─────────────────────────────────────────────────────────────────┘

     ┌─────────────────────────────────────────────┐
     │           @dataclass                        │
     │         EvaluatorConfig                     │
     ├─────────────────────────────────────────────┤
     │ + dotnet_url: str                          │
     │ + python_url: str                          │
     │ + judge_provider: str                      │
     │ + openai_model: str                        │
     │ + openai_api_key: Optional[str]            │
     │ + ollama_host: str                         │
     │ + ollama_model: str                        │
     ├─────────────────────────────────────────────┤
     │ + from_environment() -> EvaluatorConfig    │
     │ + is_openai_available() -> bool            │
     │ + is_ollama_enabled() -> bool              │
     │ + is_heuristic_mode() -> bool              │
     └─────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     Communication Layer                          │
└─────────────────────────────────────────────────────────────────┘

     ┌─────────────────────────────────────────────┐
     │           ChatbotClient                     │
     ├─────────────────────────────────────────────┤
     │ - base_url: str                            │
     │ - timeout: float                           │
     ├─────────────────────────────────────────────┤
     │ + ask_question(client, question) -> str    │
     └─────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Scoring Strategy Layer                      │
└─────────────────────────────────────────────────────────────────┘

              ┌─────────────────────────────┐
              │   <<abstract>>              │
              │   ScoringStrategy           │
              ├─────────────────────────────┤
              │ + evaluate() -> Dict        │
              └──────────┬──────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ OpenAIJudge  │ │ OllamaJudge  │ │HeuristicJudge│
├──────────────┤ ├──────────────┤ ├──────────────┤
│- api_key     │ │- host        │ │(no state)    │
│- model       │ │- model       │ │              │
├──────────────┤ ├──────────────┤ ├──────────────┤
│+ evaluate()  │ │+ evaluate()  │ │+ evaluate()  │
└──────────────┘ └──────────────┘ └──────────────┘

     ┌─────────────────────────────────────────────┐
     │      ScoringStrategyFactory                 │
     ├─────────────────────────────────────────────┤
     │ + create(provider, **kwargs) -> Strategy   │
     └─────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       Orchestration Layer                        │
└─────────────────────────────────────────────────────────────────┘

     ┌─────────────────────────────────────────────┐
     │           @dataclass                        │
     │         EvaluationResult                    │
     ├─────────────────────────────────────────────┤
     │ + prompt_id: str                           │
     │ + question: str                            │
     │ + dotnet_response: str                     │
     │ + python_response: str                     │
     │ + dotnet_score: float                      │
     │ + python_score: float                      │
     │ + winner: str                              │
     │ + judge_comment: str                       │
     ├─────────────────────────────────────────────┤
     │ + to_dict() -> Dict                        │
     └─────────────────────────────────────────────┘

     ┌─────────────────────────────────────────────┐
     │           JudgeEvaluator                    │
     ├─────────────────────────────────────────────┤
     │ - config: EvaluatorConfig                  │
     │ - dotnet_client: ChatbotClient             │
     │ - python_client: ChatbotClient             │
     │ - scoring_strategy: ScoringStrategy        │
     │ - prompts: List[Dict]                      │
     ├─────────────────────────────────────────────┤
     │ + evaluate_all() -> List[EvaluationResult] │
     │ + generate_report(results) -> str          │
     │ + save_results(results, output_dir)        │
     │ - _evaluate_single_prompt() -> Result      │
     │ - _generate_summary() -> str               │
     │ - _generate_detailed_results() -> str      │
     └─────────────────────────────────────────────┘
```

## 3. Sequence Diagram: Full Evaluation Flow

```
User          Entry         Judge          Chatbot       Scoring
              Point      Evaluator         Client       Strategy
 │              │            │               │             │
 │─run_eval.py─▶│            │               │             │
 │              │            │               │             │
 │              │─create────▶│               │             │
 │              │            │               │             │
 │              │            │─create────────▶│             │
 │              │            │               │             │
 │              │            │─create_strategy─────────────▶│
 │              │            │               │             │
 │              │─evaluate_all()────────────▶│             │
 │              │            │               │             │
 │              │            │   ┌───────────┐             │
 │              │            │───│for prompt │             │
 │              │            │   └───────────┘             │
 │              │            │               │             │
 │              │            │─ask(.NET)─────▶│             │
 │              │            │               │             │
 │              │            │◀─response──────│             │
 │              │            │               │             │
 │              │            │─ask(Python)───▶│             │
 │              │            │               │             │
 │              │            │◀─response──────│             │
 │              │            │               │             │
 │              │            │─evaluate──────────────────▶│
 │              │            │               │             │
 │              │            │◀─scores────────────────────│
 │              │            │               │             │
 │              │◀─results────────────────────│             │
 │              │            │               │             │
 │              │─save_results()────────────▶│             │
 │              │            │               │             │
 │              │            │─generate_report()           │
 │              │            │               │             │
 │              │            │─write files   │             │
 │              │            │               │             │
 │◀─complete────│            │               │             │
 │              │            │               │             │
```

## 4. Strategy Pattern Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    Client Code (judge.py)                     │
│                                                               │
│  config = EvaluatorConfig.from_environment()                 │
│                                                               │
│  strategy = ScoringStrategyFactory.create(                   │
│      provider=config.judge_provider,                         │
│      openai_api_key=config.openai_api_key,                   │
│      openai_model=config.openai_model,                       │
│      ollama_host=config.ollama_host,                         │
│      ollama_model=config.ollama_model                        │
│  )                                                            │
│                                                               │
│  result = await strategy.evaluate(                           │
│      question,                                               │
│      dotnet_response,                                        │
│      python_response,                                        │
│      expected_criteria                                       │
│  )                                                            │
└──────────────────────────────────────────────────────────────┘
                           │
                           │ factory creates
                           ▼
        ┌──────────────────────────────────┐
        │  ScoringStrategyFactory.create() │
        └──────────────────┬───────────────┘
                           │
                           │ based on provider
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
   ┌────────────┐   ┌────────────┐   ┌────────────┐
   │  OpenAI    │   │   Ollama   │   │ Heuristic  │
   │   Judge    │   │    Judge   │   │   Judge    │
   │            │   │            │   │            │
   │ evaluate() │   │ evaluate() │   │ evaluate() │
   └────────────┘   └────────────┘   └────────────┘
          │                │                │
          └────────────────┴────────────────┘
                           │
                           │ returns
                           ▼
                  ┌─────────────────┐
                  │  Dict[str, Any] │
                  ├─────────────────┤
                  │ dotnet_score    │
                  │ python_score    │
                  │ winner          │
                  │ comment         │
                  └─────────────────┘
```

## 5. Dependency Graph

```
run_evaluation.py
       │
       ├─imports─▶ evaluator.__init__
       │                  │
       │                  ├─exports─▶ JudgeEvaluator
       │                  │                │
       │                  │                ├─uses─▶ config.EvaluatorConfig
       │                  │                │
       │                  │                ├─uses─▶ http_client.ChatbotClient
       │                  │                │
       │                  │                └─uses─▶ scoring.ScoringStrategyFactory
       │                  │                                │
       │                  │                                ├─creates─▶ OpenAIJudge
       │                  │                                │
       │                  │                                ├─creates─▶ OllamaJudge
       │                  │                                │
       │                  │                                └─creates─▶ HeuristicJudge
       │                  │
       │                  └─exports─▶ EvaluatorConfig
       │
       └─runs───▶ asyncio.run(main())
                          │
                          └─awaits─▶ evaluator.evaluate_all()
```

## 6. File Dependency Matrix

```
┌─────────────┬────────┬────────┬────────┬────────┬────────┐
│             │config  │http_   │scoring │judge   │run_    │
│             │.py     │client  │.py     │.py     │eval.py │
├─────────────┼────────┼────────┼────────┼────────┼────────┤
│config.py    │   -    │   0    │   0    │   1    │   1    │
├─────────────┼────────┼────────┼────────┼────────┼────────┤
│http_client  │   0    │   -    │   0    │   1    │   0    │
├─────────────┼────────┼────────┼────────┼────────┼────────┤
│scoring.py   │   0    │   0    │   -    │   1    │   0    │
├─────────────┼────────┼────────┼────────┼────────┼────────┤
│judge.py     │   1    │   1    │   1    │   -    │   1    │
├─────────────┼────────┼────────┼────────┼────────┼────────┤
│run_eval.py  │   1    │   0    │   0    │   1    │   -    │
└─────────────┴────────┴────────┴────────┴────────┴────────┘

Legend:
  0 = No dependency
  1 = Direct dependency
  - = Self
```

## 7. Before vs After Architecture

### Before (Monolithic)
```
┌────────────────────────────────────────────┐
│     llm-judge-evaluator.py (230 lines)     │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  LLMJudgeEvaluator class             │ │
│  │                                      │ │
│  │  - Config (inline)                   │ │
│  │  - HTTP requests (inline)            │ │
│  │  - OpenAI judge (inline)             │ │
│  │  - Ollama judge (inline)             │ │
│  │  - Heuristic judge (inline)          │ │
│  │  - Report generation (inline)        │ │
│  │  - File I/O (inline)                 │ │
│  │                                      │ │
│  │  Everything tightly coupled          │ │
│  └──────────────────────────────────────┘ │
└────────────────────────────────────────────┘

Problems:
❌ Hard to test
❌ Hard to extend
❌ Mixed concerns
❌ No type safety
❌ Poor reusability
```

### After (Clean Architecture)
```
┌─────────────────────────────────────────────────────────┐
│              evaluator/ (594 lines, 5 files)             │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Config     │  │ HTTP Client  │  │   Scoring    │ │
│  │              │  │              │  │  Strategies  │ │
│  │ 44 lines     │  │ 47 lines     │  │  317 lines   │ │
│  │ Isolated     │  │ Reusable     │  │  Pluggable   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│              ┌──────────────────────┐                   │
│              │   Judge Evaluator    │                   │
│              │                      │                   │
│              │     186 lines        │                   │
│              │   Orchestration      │                   │
│              └──────────────────────┘                   │
└─────────────────────────────────────────────────────────┘

Benefits:
✅ Easy to test (DI)
✅ Easy to extend (strategies)
✅ Clear concerns
✅ Full type safety
✅ High reusability
```

## 8. Extensibility Example

### Adding a New Judge Strategy

```
Step 1: Implement Strategy
┌────────────────────────────────────────────────┐
│  scoring.py                                    │
│                                                │
│  class AnthropicJudge(ScoringStrategy):       │
│      def __init__(self, api_key, model):      │
│          self.api_key = api_key               │
│          self.model = model                   │
│                                                │
│      async def evaluate(...) -> Dict:          │
│          # Call Anthropic API                  │
│          return {                             │
│              "dotnet_score": ...,             │
│              "python_score": ...,             │
│              "winner": ...,                   │
│              "comment": ...                   │
│          }                                    │
└────────────────────────────────────────────────┘

Step 2: Update Factory
┌────────────────────────────────────────────────┐
│  scoring.py                                    │
│                                                │
│  class ScoringStrategyFactory:                │
│      @staticmethod                             │
│      def create(provider, **kwargs):          │
│          if provider == "anthropic":          │
│              return AnthropicJudge(...)       │
│          # ... existing strategies            │
└────────────────────────────────────────────────┘

Step 3: Use It
┌────────────────────────────────────────────────┐
│  export JUDGE_PROVIDER=anthropic              │
│  export ANTHROPIC_API_KEY=sk-...              │
│  python run_evaluation.py                     │
└────────────────────────────────────────────────┘

That's it! No changes to:
  ✅ judge.py
  ✅ config.py
  ✅ http_client.py
  ✅ run_evaluation.py
```

---

**These diagrams illustrate the transformation from a monolithic script to a clean, modular architecture following professional software engineering practices.**
