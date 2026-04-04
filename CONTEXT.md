# RAG Benchmark Multi-Language — Context Document

## Project Overview

**Purpose:** Compare RAG (Retrieval-Augmented Generation) implementations across two different tech stacks — Python (LangChain) and C# (.NET Semantic Kernel) — in a candidate matching/recruitment workflow.

**Core Hypothesis:** Two parallel implementations using identical business logic should produce comparable results. This project validates architectural parity, performance characteristics, and output quality across languages.

**Scope:** End-to-end RAG pipeline: embeddings generation → vector storage → semantic search → LLM augmentation → structured output.

---

## What Was Built

### 1. Dual-Stack API Services

#### Python API (LangChain)
- **Framework:** FastAPI
- **RAG Engine:** LangChain
- **Port:** 8000
- **Endpoint:** `POST /chat` with `{"question": "..."}` payload
- **Output:** `{"answer": "..."}` (structured candidate matching response)

#### C# API (Semantic Kernel)
- **Framework:** ASP.NET Minimal APIs
- **.NET Version:** 10
- **RAG Engine:** Microsoft.Extensions.AI (MEAI)
- **Port:** 5000
- **Endpoint:** `POST /chat` with identical JSON contract
- **Output:** Matching response structure to Python

### 2. Shared Infrastructure

#### Embeddings Service (Python FastAPI)
- **Model:** HuggingFace `sentence-transformers/all-MiniLM-L6-v2`
- **Port:** 8080
- **Endpoints:**
  - `POST /embed` — Generate embeddings for text array
  - `GET /instruction-pairs` — Retrieve training instruction pairs
- **Why separate:** Ensures both APIs use identical vector representations (critical for parity testing)

#### Vector Database (Qdrant)
- **Port:** 6333
- **Purpose:** Store candidate embeddings for semantic search
- **Collection:** `candidates`

#### LLM Provider (Ollama)
- **Port:** 11434
- **Default Model:** `llama3:8b` (configurable via `config/common.yaml`)
- **Temperature:** 0 (deterministic, required for benchmarking)

### 3. Evaluation Framework

#### LLM-as-a-Judge Scoring
- **Multi-run evaluation:** Each question evaluated 3+ times for statistical robustness
- **Judges Supported:**
  - Ollama (local, free)
  - OpenAI (remote, production-grade)
  - Heuristic baseline
- **Metrics Aggregated:**
  - Mean score (per implementation)
  - Standard deviation
  - Judge agreement percentage
- **Scoring Scale:** 0–10 (lower/higher depends on eval prompt)

#### Performance Benchmarking (K6)
- **Smoke Test:** 1 user, 30 seconds (basic validation)
- **Load Test:** 10–20 concurrent users, ~14 minutes
- **Stress Test:** 10–100 escalating users, ~21 minutes
- **Metrics:** Throughput, latency (p50/p95/p99), error rates

#### Test Suites
- **Integration Tests:** End-to-end flow validation (both stacks)
- **Parity Tests:** Verify Python and .NET produce identical outputs given same inputs
- **Normalization Tests:** Technology-specific processing differences (JSON parsing, field mapping)

---

## Data & Configuration

### Candidate Dataset
- **Format:** JSON files (6 sample résumés preprocessed)
- **Location:** `data/input/`
- **Usage:** Indexed into vector database, retrieved per question
- **PII Handling:** Demo/CV data, noted in docs

### Configuration (YAML)
**File:** `config/common.yaml`

**Key Sections:**
- `python_api.port` → FastAPI bind port
- `dotnet_api.urls` → ASP.NET URL
- `embeddings_service.url` → Shared embeddings endpoint
- `vector_storage.type` → "native" (Chroma for Python) or "qdrant"
- `llm_provider.provider` → "ollama" or "openai"
- `llm_provider.model` → Model name (e.g., `llama3:8b`)
- `qdrant.url` → Vector DB endpoint

**Evaluation Config:** `config/evaluation.yaml`
- `judge_provider` → ollama/openai
- `judge_runs` → Number of evaluation passes
- `temperature` → 0 (pinned for determinism)
- `timeout_seconds` → API/judge timeout
- `tie_tolerance` → Score difference threshold for "tie"

### Prompts
**System Prompt:** `data/prompts/chat_system.md`
- Recruiter AI persona
- Task description (candidate evaluation)

**Human Prompt Template:** `data/prompts/chat_human.md`
- Context injection format
- Variable substitution for candidate info

**Judge Prompt:** `data/prompts/evaluation_judge.md`
- LLM-as-a-Judge instructions
- Scoring rubric

---

## Startup Sequence (Required Order)

1. **Docker services** (must run first for vector DB + LLM)
   ```bash
   docker compose -f infra/docker/docker-compose.qdrant.yml up -d
   docker compose -f infra/docker/docker-compose.ollama.yml up -d
   ```

2. **Ollama model pull** (once per model change)
   ```bash
   docker exec -it ollama ollama pull llama3:8b
   ```

3. **Embeddings server** (dependency for both APIs)
   ```bash
   python -m services.embeddings_python.serve
   ```

4. **Either API** (independent, can run one or both)
   - Python: `python -m src.python.langchain_api`
   - .NET: `dotnet run --project src/dotnet/Semantic.Kernel.Api.csproj`

5. **Quality evaluation** (optional, requires both APIs running)
   ```bash
   python benchmarks/run_evaluation.py
   ```

6. **Performance testing** (optional, requires both APIs running)
   ```bash
   ./benchmarks/run-benchmarks.sh both
   ```

---

## Web UI (React + Vite)

**Location:** `ui/`

**Purpose:** Interactive demo splitting screen between Python and .NET responses side-by-side

**Features:**
- Split-screen layout (Python left, .NET right, "VS" divider)
- Simultaneous API calls (both receive question at same time)
- Elapsed time per response (milliseconds)
- Typewriter animation on bot responses
- Status indicators (online/offline checks for :8000 and :5000)
- Quick suggestion prompts
- 4-suggestion shortcuts pre-populated

**How to Run:**
```bash
cd ui && npx vite --port 3000
```
**Access:** http://localhost:3000

**Design Approach:**
- Pure CSS (no frameworks like Tailwind)
- Dark theme inspired by Vercel/Linear
- Color palette:
  - Base: `#0d0f14` (very dark blue-gray)
  - Python accent: `#3ecf8e` (emerald green)
  - .NET accent: `#7c6af7` (medium purple)
  - Text primary: `#e8eaf0` (off-white)
  - Text muted: `#555c73` (dim gray)

---

## Testing & Validation

### What Was Tested

1. **Functional Parity**
   - Same question → both APIs should return semantically similar candidate recommendations
   - JSON structure consistency across implementations
   - Error handling alignment

2. **Performance Baseline**
   - Latency under varying concurrency
   - Throughput comparison (requests/sec)
   - Resource utilization

3. **Output Quality**
   - LLM judge scored responses on relevance, accuracy, completeness
   - Statistical aggregation across multiple judge runs
   - Tie detection and winner determination

### Results Location
- **Quality Reports:** `benchmarks/results/evaluation_report.md` + `.json`
- **Performance Results:** `benchmarks/results/{dotnet,python}/` (K6 HTML/JSON output)
- **Logs:** `benchmarks/logs/evaluation_YYYYMMDD_HHMMSS.log`

---

## Architecture Diagram (Conceptual)

```
┌─────────────────────────────────────────────────────────────┐
│                         Web UI (React)                      │
│                    localhost:3000 / split                   │
└──────────────────┬──────────────────────┬──────────────────┘
                   │                      │
        ┌──────────▼────────┐   ┌────────▼──────────┐
        │  Python API       │   │   .NET API        │
        │  (LangChain)      │   │ (Semantic Kernel) │
        │  :8000            │   │ :5000             │
        └───────┬──────────┘   └────────┬──────────┘
                │                       │
                └───────────┬───────────┘
                            │
        ┌───────────────────┴──────────────────┐
        │                                      │
    ┌───▼─────────────────┐    ┌──────────────▼──┐
    │ Embeddings Service  │    │ Vector Storage   │
    │ (HuggingFace)       │    │ (Qdrant)         │
    │ :8080               │    │ :6333            │
    └─────────────────────┘    └──────────────────┘
                                      ▲
                                      │
                            ┌─────────▼────────┐
                            │ Ollama (LLM)     │
                            │ :11434           │
                            │ llama3:8b (etc.) │
                            └──────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     Evaluation Suite                         │
│  ┌─────────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  LLM-as-Judge   │  │  K6 Load     │  │  Parity /    │   │
│  │  (Ollama/OpenAI)│  │  Testing     │  │  Integration │   │
│  │  Scoring Runs   │  │  (Metrics)   │  │  Tests       │   │
│  └─────────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Development Philosophy

**KISS Principles:**
- Minimal dependencies per service
- Single responsibility (embeddings = embeddings only, not bundled with APIs)
- Stateless APIs (all state in vector DB or config)
- Configuration-first (YAML drives behavior, no hardcoding)

**Technology Choices:**
- **Python:** FastAPI (fast, async-native, minimal boilerplate)
- **.NET:** Minimal APIs + MEAI (modern, lightweight, cloud-ready)
- **Embeddings:** Shared external service (language-agnostic, reproducible)
- **Vector Store:** Qdrant (production-grade, docker-native)
- **LLM:** Ollama (local, free, deterministic) + OpenAI (production option)
- **Benchmarking:** K6 (lightweight, scriptable load testing) + LLM judge (semantic quality)

---

## Key Findings / Observations

> **Note:** This section to be populated after evaluation runs complete. Include:
> - Winner (Python or .NET) by: quality score, latency, throughput
> - Unexpected parity gaps or alignment surprises
> - Performance characteristics (which API scales better?)
> - Any framework-specific quirks or workarounds

---

## Known Limitations & Next Steps

- **Vector Store Choice:** "Native" mode uses Chroma (Python) vs in-memory (C#); Qdrant mode aligns both
- **Model Dependency:** Ollama model must be pre-pulled; no auto-download
- **Determinism:** All evaluations pinned to temperature=0; non-deterministic LLM paths not tested
- **Dataset:** 6 demo résumés; production evaluation requires larger dataset
- **UI:** React demo for interactive testing; no persistent evaluation history persisted in UI

---

## Files & Directory Structure Reference

```
llm-candidate-rag-benchmark-multilang/
├── config/common.yaml                    # Centralized config (ports, models, providers)
├── config/evaluation.yaml                # Evaluation-specific settings
├── data/
│   ├── input/                           # Candidate JSONs
│   ├── prompts/                         # System, human, judge prompts (MD files)
│   ├── instructions/                    # embeddings.jsonl, llm.jsonl for training
│   └── schema/                          # candidate_record schema
├── services/embeddings_python/          # Shared embeddings microservice
├── src/python/                          # LangChain RAG (api/, core/)
├── src/dotnet/                          # MEAI RAG (Api/, Core/)
├── ui/                                  # React + Vite demo
├── benchmarks/
│   ├── evaluator/                       # LLM judge, scoring, scoring.py
│   ├── k6/                              # Load test scripts (JS)
│   ├── run_evaluation.py                # Main evaluation entry
│   ├── results/                         # Output reports
│   └── logs/                            # Evaluation logs
├── tests/{python,dotnet}/               # Integration, parity, normalization tests
├── infra/docker/                        # docker-compose files (Qdrant, Ollama)
└── README.md
```

---

## Commands Quick Reference

| Task | Command |
|------|---------|
| Start Qdrant | `docker compose -f infra/docker/docker-compose.qdrant.yml up -d` |
| Start Ollama | `docker compose -f infra/docker/docker-compose.ollama.yml up -d` |
| Pull model | `docker exec -it ollama ollama pull llama3:8b` |
| Embeddings server | `python -m services.embeddings_python.serve` |
| Python API | `python -m src.python.langchain_api` |
| .NET API | `dotnet run --project src/dotnet/Semantic.Kernel.Api.csproj` |
| Quality eval | `python benchmarks/run_evaluation.py` |
| Performance eval | `./benchmarks/run-benchmarks.sh both` |
| Web UI | `cd ui && npx vite --port 3000` |

---

## Additional Notes for Blog

- **Target Audience:** ML engineers, architects comparing cross-language RAG implementations, teams weighing Python vs .NET for LLM applications
- **Unique Angle:** Multi-language parity testing, shared embeddings as single source of truth, deterministic evaluation with LLM-as-Judge
- **Code Availability:** Open-source (GitHub link TBD)
- **Production Readiness:** Framework code is production-ready; dataset is demo-scale; evaluation methodology is reproducible
