# LLM Candidate RAG Benchmark - Multi-Language

A benchmarking project to compare RAG (Retrieval-Augmented Generation) implementations for candidate matching using two different tech stacks:

- **Python** with LangChain framework
- **C#** with Microsoft.Extensions.AI (MEAI)

## Current Implementation Status

🟢 **Embeddings Service** - Ready  
🟢 **Python API** - Ready  
🟢 **C# API** - Ready  
🟢 **Benchmark Suite** - Ready  

## Architecture Overview

```
llm-candidate-rag-benchmark-multilang/
├── config/
│   └── common.yaml            # Centralized configuration
├── data/
│   ├── input/                 # Preprocessed candidates dataset (JSON files)
│   ├── instructions/          # Training datasets
│   │   ├── embeddings.jsonl   # Embeddings Instructions
│   │   └── llm.jsonl          # Finetuning
│   ├── prompts/               # LLM prompt templates
│   │   ├── chat_system.md     # System prompt for recruiter AI
│   │   └── chat_human.md      # Human prompt with context template
│   └── schema/                # Data structure definitions
├── services/
│   └── embeddings_python/     # Shared embeddings microservice
│       ├── embeddings_api.py  # FastAPI server
│       └── serve.py           # Entry point
├── src/
│   ├── python/                # Python RAG implementation (LangChain)
│   │   ├── api/               # FastAPI endpoints
│   │   └── core/              # Application logic, domain, infrastructure
│   └── dotnet/                # .NET RAG implementation (Microsoft.Extensions.AI)
│       ├── Api/               # ASP.NET endpoints
│       └── Core/              # Application, domain, infrastructure
├── tests/
│   ├── python/                # Python tests
│   │   ├── integration/       # End-to-end validation
│   │   ├── parity/            # Python/NET behavior comparison
│   │   └── normalization/     # Technology normalization
│   └── dotnet/                # .NET tests
│       ├── Integration/       # End-to-end validation
│       ├── Parity/            # Python/NET behavior comparison
│       └── Normalization/     # Technology normalization
├── benchmarks/
│   ├── evaluator/             # LLM-as-a-Judge framework
│   │   ├── judge.py           # Evaluation orchestrator
│   │   ├── scoring.py         # Judge providers (Ollama, OpenAI, Heuristic)
│   │   └── http_client.py     # API client
│   ├── k6/                    # Load testing scripts
│   ├── results/               # Benchmark reports
│   └── run-benchmarks.*       # Automation scripts
├── infra/
│   └── docker/                # Docker Compose for Qdrant, Ollama
├── pyproject.toml             # Python dependencies
└── README.md
```

**Key Principles:**
- **Multi-language parity**: Python and .NET implement identical RAG pipelines
- **Shared embeddings**: Single embeddings service ensures consistent vector representations
- **Benchmark-first**: LLM-as-a-Judge evaluator validates quality; K6 tests validate performance
- **Integration over unit**: Tests focus on end-to-end behavior and cross-stack parity

## Services

### Embeddings Service (Python)

A FastAPI microservice that provides text embeddings using HuggingFace transformers. This service is shared between both Python and C# implementations to ensure consistent vector representations.

**Features:**
- REST API for text embedding generation
- Instruction pairs endpoint for training data
- Configurable via YAML
- Uses `sentence-transformers/all-MiniLM-L6-v2` model

**Endpoints:**
- `POST /embed` - Generate embeddings for text array
- `GET /instruction-pairs` - Retrieve training instruction pairs

## Getting Started

### Prerequisites

- Python 3.10+ with virtual environment
- YAML configuration file at `config/common.yaml`

**macOS quick notes**

- **Python 3.13 (required):** 
  - Check version: `python3 --version` (needs **3.10-3.13**, Python 3.14+ not yet supported by dependencies)
  - Install if needed: `brew install python@3.13`
  - Create venv: `python3.13 -m venv .venv`
  - Activate: `source .venv/bin/activate`

- **.NET SDK (optional, for .NET API):**
  - Verify: `dotnet --version` (project targets **.NET 10**)

- **Docker Desktop (required for Qdrant/Ollama):**
  - Install: `brew install --cask docker`
  - Or download from [docker.com](https://www.docker.com/products/docker-desktop)
  - Start Docker Desktop app before running services

- **Environment variables:** set `OPENAI_API_KEY` if using the OpenAI judge; check `config/common.yaml` for `OLLAMA`/`QDRANT` ports and URLs.

### Running the Embeddings Service

1. **Create and activate your Python virtual environment:**
  ```bash
  # Create (Unix/macOS)
  python3 -m venv .venv
  # Activate (Unix/macOS)
  source .venv/bin/activate

  # Windows (PowerShell)
  .venv\Scripts\Activate.ps1
  ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Start the embeddings service:**
   
   **From Project Root (recommended)**
   ```bash
   python -m services.embeddings_python.serve
   ```

   The service will start on the host/port configured in `config/common.yaml` under `embeddings_service` section.

### Running the APIs

> **Required startup order:** Docker services → Ollama model → Embeddings server → API

#### 1. Start Docker services

```bash
docker compose -f infra/docker/docker-compose.qdrant.yml up -d
docker compose -f infra/docker/docker-compose.ollama.yml up -d
```

#### 2. Pull the Ollama model

The model is configured in `config/common.yaml` under `llm_provider.model`. Pull it before starting any API:

```bash
# Default model (see config/common.yaml > llm_provider.model)
docker exec -it ollama ollama pull llama3:8b
```

> If you change the model in `common.yaml`, pull that model instead.

#### 3. Start the Embeddings server

```bash
# Activate venv first (if not already activated)
.venv\Scripts\Activate.ps1          # Windows
source .venv/bin/activate            # macOS/Linux

python -m services.embeddings_python.serve
```

The service starts on the host/port configured in `config/common.yaml` under `embeddings_service`.

#### 4. Start an API

**Python API (LangChain):**
```bash
python -m src.python.langchain_api
```

**C# API (Semantic Kernel):**
```bash
dotnet run --project src/dotnet/Semantic.Kernel.Api.csproj
```

Quality evaluation supports multi-run judging (`JUDGE_RUNS`) and reports aggregated metrics (mean score, standard deviation, and judge agreement %). See [`benchmarks/README.md`](benchmarks/README.md) for the statistical methodology, baseline settings, and the exact benchmark commands.
**Output:**
- `benchmarks/results/evaluation_report.md` - Human-readable report with statistical metrics
- `benchmarks/results/evaluation_results.json` - Detailed scores, agreement %, std dev
- `benchmarks/logs/evaluation_YYYYMMDD_HHMMSS.log` - Error traces

### Performance Tests (K6)

Load testing to measure throughput, latency, and resource usage under various loads.

**Run performance benchmarks:**

```bash
# Windows (PowerShell)
.\benchmarks\run-benchmarks.ps1 both

# Linux/macOS
./benchmarks/run-benchmarks.sh both

# Test only .NET or Python
./benchmarks/run-benchmarks.sh dotnet
./benchmarks/run-benchmarks.sh python
```

**What it runs:**
- **Smoke test**: Basic functionality validation (1 user, 30s)
- **Load test**: Normal load performance (10-20 users, 14min)
- **Stress test**: Breaking point discovery (10-100 users, 21min)

**Prerequisites:**
- **K6**: `winget install k6` (Windows) or `brew install k6` (macOS)
- APIs running (ports configured in `config/common.yaml`)

📖 **Full documentation**: See [`benchmarks/README.md`](benchmarks/README.md) for detailed instructions and configuration options.
## Evaluation

This project includes a statistically robust benchmark suite to compare .NET and Python implementations.

### Methodology

- Each prompt is evaluated multiple times (`JUDGE_RUNS`, recommended: 3).
- Scores (0–10) are averaged per implementation.
- Standard deviation and agreement percentage are reported.
- The winner is determined **objectively by mean score**, not by self-reported LLM output.
- All evaluations must run with **temperature = 0** for deterministic behavior.

Detailed evaluation design and statistical explanation can be found in `benchmarks/README.md`.

## Running Benchmarks

### Start Required Services

```bash
# 1. Start Docker containers
docker compose -f infra/docker/docker-compose.qdrant.yml up -d
docker compose -f infra/docker/docker-compose.ollama.yml up -d

# 2. Pull the Ollama model (see llm_provider.model in config/common.yaml)
docker exec -it ollama ollama pull llama3:8b

# 3. Start the embeddings server
python -m services.embeddings_python.serve
```

## Start APIs

```bash
# .NET (Semantic Kernel)
dotnet run --project src/dotnet/Semantic.Kernel.Api.csproj

# Python (LangChain)
python -m src.python.langchain_api
```

## Quality Evaluation

```bash
export JUDGE_PROVIDER=ollama
export JUDGE_RUNS=3
export OLLAMA_MODEL=llama3:8b

python benchmarks/run_evaluation.py
```

Results are written to:

- `benchmarks/results/evaluation_report.md`
- `benchmarks/results/evaluation_results.json`

## Performance Testing

```bash
# Windows
.\benchmarks\run-benchmarks.ps1 both

# Linux/macOS
./benchmarks/run-benchmarks.sh both
```

Performance results are stored under:

- `benchmarks/results/dotnet/`
- `benchmarks/results/python/`

## Development Philosophy

This project follows **KISS principles** for microservices - simple, focused, and maintainable code without over-engineering. Each service has a single responsibility and minimal dependencies.