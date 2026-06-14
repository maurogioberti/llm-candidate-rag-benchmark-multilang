# LLM Candidate RAG Benchmark - Multi-Language

A benchmarking project to compare RAG (Retrieval-Augmented Generation) implementations for candidate matching using two different tech stacks:

- **Python** with LangChain framework
- **C#** with Microsoft.Extensions.AI (MEAI)

## Purpose

This project was created for educational purposes. It supports a technical talk and provides a practical codebase for developers who want to better understand RAG architectures, retrieval pipelines, and LLM evaluation approaches across different implementation styles.

## Background

The project comes from a real-world benchmarking talk focused on comparing Python and .NET implementations of the same RAG system. The goal is to make the tradeoffs visible through working code, shared infrastructure, and repeatable evaluation.

## Philosophy

The central idea behind this repository is that architecture matters more than language. Python and .NET are both valid tools; what matters most is system design, consistency, observability, and clarity. This repository is intended to support learning, experimentation, and informed technical discussion rather than language advocacy.

## Attribution

This repository is released under the MIT License. If you use it in talks, articles, demos, internal experiments, or derivative educational work, attribution is appreciated as a professional courtesy, but it is not required by the license.

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

- Python 3.10 or newer. The project metadata declares `requires-python = ">=3.10"`.
- .NET SDK 10.0 or newer, required only for the .NET API.
- Docker Desktop, required for Qdrant and Ollama.
- K6, required only for performance benchmarks.
- YAML configuration file at `config/common.yaml`.

The default local LLM is configured in `config/common.yaml` under `llm_provider.model` as `llama3:8b`.

### macOS Setup

These commands assume a clean macOS machine using zsh or bash.

#### 1. Clone the repository

```bash
git clone https://github.com/maurogioberti/llm-candidate-rag-benchmark-multilang.git
cd llm-candidate-rag-benchmark-multilang
```

#### 2. Install Homebrew Python

macOS may include an older system Python, such as Python 3.9. That is fine as long as this project uses a Python virtual environment created with Python 3.10 or newer.

Use an explicit Homebrew interpreter when creating the virtual environment:

```bash
brew install python@3.13
"$(brew --prefix python@3.13)/bin/python3.13" --version
```

The global `python3` command does not need to point to Homebrew Python.

#### 3. Create and activate the Python virtual environment

```bash
"$(brew --prefix python@3.13)/bin/python3.13" -m venv .venv
source .venv/bin/activate
```

Verify that the active `python` is inside this repository:

```bash
python --version
which python
python -m pip --version
```

`which python` should print a path ending in:

```text
llm-candidate-rag-benchmark-multilang/.venv/bin/python
```

#### 4. Upgrade packaging tools and install dependencies

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
```

`python -m pip install -e .` installs this project and the dependencies declared in `pyproject.toml` into the active virtual environment.

Optional dependency check:

```bash
python -c "import uvicorn, fastapi, dataclasses_json; print('Python dependencies OK')"
```

#### 5. Install and start Docker Desktop

```bash
brew install --cask docker
```

Open Docker Desktop from Applications and wait until it is running before starting Qdrant or Ollama.

Check which Docker Compose command is available:

```bash
docker compose version
docker-compose --version
```

`docker compose` is the current Docker Compose plugin syntax. `docker-compose` is the older standalone syntax. Use whichever one is installed on your machine.

#### 6. Optional macOS tools for benchmarks

```bash
brew install k6
```

### Windows Setup

Use PowerShell from the repository root.

```powershell
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
python --version
where python
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
```

Install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop), then start Docker Desktop before running the infrastructure containers.

For performance benchmarks, install K6:

```powershell
winget install k6
```

### Startup Order

Start services in this order:

```text
Docker Desktop
-> Qdrant and Ollama containers
-> Pull and verify Ollama model
-> Python embeddings service
-> Python and/or .NET API
-> Benchmarks
```

The embeddings service must be running before either API starts because both implementations use it to produce consistent vector embeddings.

> **Important:** Starting the Ollama container does not download the model. The model must be pulled separately before either API can generate responses.

### Start Infrastructure

From the repository root:

```bash
docker compose -f infra/docker/docker-compose.qdrant.yml up -d
docker compose -f infra/docker/docker-compose.ollama.yml up -d
```

If your machine only has the older standalone Compose command, use:

```bash
docker-compose -f infra/docker/docker-compose.qdrant.yml up -d
docker-compose -f infra/docker/docker-compose.ollama.yml up -d
```

### Pull Ollama Model

The model is configured in `config/common.yaml` under `llm_provider.model`. The current value is `llama3:8b`.

The Ollama Docker Compose file uses the container name `ollama`, so the commands below run inside that container.

Check which models are already installed:

```bash
docker exec -it ollama ollama list
```

Pull the configured model:

```bash
docker exec -it ollama ollama pull llama3:8b
```

Verify that the model is now available:

```bash
docker exec -it ollama ollama list
```

Only start or test the Python and .NET APIs after the configured model appears in the list.

If you change `llm_provider.model`, run the same commands with that model name instead.

The Ollama Compose file stores models in a persistent Docker volume named `ollama`, mounted at `/root/.ollama`, so downloaded models should survive normal container restarts.

### Start Embeddings Service

Open a terminal from the repository root and activate the Python virtual environment.

macOS/Linux:

```bash
source .venv/bin/activate
python -m services.embeddings_python.serve
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m services.embeddings_python.serve
```

The service starts on the host and port configured in `config/common.yaml` under `embeddings_service`.

### Start Python API

Open a second terminal from the repository root and activate the same Python virtual environment.

macOS/Linux:

```bash
source .venv/bin/activate
python -m src.python.langchain_api
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m src.python.langchain_api
```

The Python API uses the port configured in `config/common.yaml` under `python_api`.

### Start .NET API

Open another terminal from the repository root:

```bash
dotnet run --project src/dotnet/Semantic.Kernel.Api.csproj
```

The project targets `.NET 10` and uses the URL configured in `config/common.yaml` under `dotnet_api`.

### Run Benchmarks

Benchmarks require the infrastructure containers, the embeddings service, and the API or APIs under test to be running.

Quality evaluation supports multi-run judging (`JUDGE_RUNS`) and reports aggregated metrics. See [`benchmarks/README.md`](benchmarks/README.md) for the statistical methodology.

The K6 performance script runs smoke, load, and stress tests against the selected API target.

macOS/Linux:

```bash
export JUDGE_PROVIDER=ollama
export JUDGE_RUNS=3
export OLLAMA_MODEL=llama3:8b
python benchmarks/run_evaluation.py

./benchmarks/run-benchmarks.sh both
```

Windows PowerShell:

```powershell
$env:JUDGE_PROVIDER = "ollama"
$env:JUDGE_RUNS = "3"
$env:OLLAMA_MODEL = "llama3:8b"
python benchmarks/run_evaluation.py

.\benchmarks\run-benchmarks.ps1 both
```

Performance benchmark targets:

```bash
./benchmarks/run-benchmarks.sh dotnet
./benchmarks/run-benchmarks.sh python
./benchmarks/run-benchmarks.sh both
```

Results are written to:

- `benchmarks/results/evaluation_report.md`
- `benchmarks/results/evaluation_results.json`
- `benchmarks/results/dotnet/`
- `benchmarks/results/python/`

### Troubleshooting

#### Incomplete Python virtual environment

If `.venv` exists but `.venv/bin/activate` or `.venv/bin/python` is missing, the virtual environment was only partially created. Recreate it from the repository root:

```bash
deactivate 2>/dev/null || true
rm -rf .venv
"$(brew --prefix python@3.13)/bin/python3.13" -m venv .venv
source .venv/bin/activate
```

A Python virtual environment created on Windows cannot be copied to or reused on macOS. Recreate it locally.

#### Old pip cannot install editable projects

If `python -m pip install -e .` fails on a clean macOS machine, upgrade packaging tools first:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
```

#### Docker Compose command not found

If `docker compose ...` fails because Compose is not recognized, check for the legacy command:

```bash
docker compose version
docker-compose --version
```

Then use either `docker compose` or `docker-compose` consistently for the Qdrant and Ollama Compose files.

#### 404 model not found

If the Python API returns an error like:

```json
{
  "detail": "LLM/Index error: model 'llama3:8b' not found (status code: 404)"
}
```

or the .NET API receives a 404 from Ollama, Ollama is usually running and reachable, but the requested model is not installed inside the Ollama environment.

Check that the containers are running:

```bash
docker ps
```

Check which models Ollama has installed:

```bash
docker exec -it ollama ollama list
```

Check the Ollama HTTP API directly:

```bash
curl http://localhost:11434/api/tags
```

If the configured model is missing, pull it:

```bash
docker exec -it ollama ollama pull llama3:8b
```

## Development Philosophy

This project follows **KISS principles** for microservices - simple, focused, and maintainable code without over-engineering. Each service has a single responsibility and minimal dependencies.
