# LLM Candidate RAG Benchmark - Multi-Language

A benchmarking project to compare RAG (Retrieval-Augmented Generation) implementations for candidate matching using two different tech stacks:

- **Python** with LangChain framework
- **C#** with Semantic Kernel framework

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
│   ├── input/                 # Raw candidate data (JSON profiles)
│   ├── instructions/          # Training datasets
│   │   └── embeddings.jsonl    # Synthetic candidate matching examples
│   ├── prompts/               # LLM prompt templates
│   │   ├── chat_system.txt    # System prompt for recruiter AI
│   │   └── chat_human.txt     # Human prompt with context template
│   └── schema/                # Data structure definitions
├── services/
│   └── embeddings-python/     # Shared embeddings service
│       ├── config_loader.py   # YAML configuration management
│       ├── embedding_server.py # FastAPI server
│       ├── embeddings_utils.py # Utility functions
│       └── run_server.py      # Service entry point
├── src/
│   └── python/                # Python RAG implementation
├── benchmarks/
│   ├── evaluator/             # LLM-as-a-Judge evaluation framework
│   │   ├── config.py          # Configuration loader (reads common.yaml)
│   │   ├── judge.py           # Main evaluation orchestrator
│   │   ├── http_client.py     # HTTP client for chatbot endpoints
│   │   ├── scoring.py         # Scoring strategies (OpenAI, Ollama, Heuristic)
│   │   └── README.md          # Evaluator documentation
│   ├── quality-prompts.json   # HR evaluation prompts for judge
│   ├── results/               # Evaluation reports and JSON results
│   ├── run-benchmarks.ps1     # PowerShell benchmark runner
│   ├── run-benchmarks.sh      # Bash benchmark runner
│   └── k6/                    # K6 load testing scripts
├── pyproject.toml             # Python project configuration
└── README.md
```

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

### Running the Embeddings Service

1. **Activate your Python virtual environment:**
   ```powershell
   # Windows
   .venv\Scripts\Activate.ps1
   
   # Unix/macOS  
   source .venv/bin/activate
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

#### Python API (LangChain)

1. **Prerequisites:**
   - Python 3.10+ with virtual environment
   - Running embeddings service and vector database (Qdrant)
   - Installed dependencies (`pip install -e .`)

2. **Start the Python API:**
   ```bash
   python -m src.python.langchain_api
   ```

   The API will start on the host/port configured in `config/common.yaml` under `python_api` section.

#### .NET API (Semantic Kernel)

1. **What you need:**
   - .NET 8.0+ SDK installed
   - Make sure the embeddings service is running (see above)

2. **How to run the .NET API:**
   ```bash
   dotnet run --project src/dotnet/Semantic.Kernel.Api.csproj
   ```

   The API will start on the host/port you set in `config/common.yaml` under the `dotnet_api` section.

### Configuration

The service reads configuration from `config/common.yaml`. Required sections:

```yaml
embeddings_service:
  host: "0.0.0.0"
  port: 8080
  instruction_file: "embeddings.jsonl"

data:
  root: "./data"
  embeddings_instructions: "instructions"
```

## Data Structure

### Candidate Profiles (`data/input/`)
Processed JSON files with structured candidate information including:
- **GeneralInfo**: Experience, seniority, languages, location
- **SkillMatrix**: Technical competencies with proficiency levels
- **KeywordCoverage**: ATS compatibility and keyword analysis
- **Scoring**: Overall candidate evaluation metrics

### Training Data (`data/instructions/`)

**Embeddings Instructions (`embeddings.jsonl`)**  
JSONL instruction pairs for embeddings training:

```json
{
  "query": "Tech Lead backend with C1 English and mentoring experience",
  "positive": "MauroGiobertiBackendDotNetEnglishC1TechLead|GeneralInfo: 12 years, Tech Lead, mentoring, English C1",
  "negative": "JeronimoGarciaFrontendReactEnglishB2|Experience: 3 years React/Next.js, migration AngularJS→Next.js"
}
```

**Fine-tuning Data (`llm.jsonl`)**  
JSONL instruction pairs for LLM fine-tuning with conversational format.

### Prompt Templates (`data/prompts/`)
- **System Prompt**: Defines AI assistant role as senior technical recruiter
- **Human Prompt**: Template with retrieval context and query structure

## Docker Infrastructure

The project includes Docker Compose configurations for running supporting services.

### Running Services (from `infra/docker/`)

**Qdrant Vector Database:**
```bash
docker compose -f docker-compose.qdrant.yml up -d
```

**Ollama LLM Service:**
```bash
docker compose -f docker-compose.ollama.yml up -d
```

**Running Both Services:**
```bash
docker compose -f docker-compose.qdrant.yml up -d
docker compose -f docker-compose.ollama.yml up -d
```

### Service Details

- **Qdrant**: Vector database running on port `6333` (configurable via `QDRANT_HTTP_PORT`)
- **Ollama**: LLM service running on port `11434` (configurable via `OLLAMA_PORT`) with `llama3:8b` model pre-loaded

## Benchmarking

We've built a comprehensive benchmark suite to compare .NET vs Python performance and quality:

### LLM-as-a-Judge Evaluator

Automated quality evaluation of .NET vs Python responses using LLM judging with fallback to heuristics.

**Features:**
- Reads configuration from `config/common.yaml` (same as APIs)
- Three judge providers:
  - **Ollama**: Local LLM evaluation (default, requires Ollama running)
  - **OpenAI**: GPT-based evaluation (requires OPENAI_API_KEY)
  - **Heuristic**: Rule-based scoring (no external LLM needed)
- Evaluates both implementations against 10 HR evaluation prompts
- Generates Markdown report and JSON results
- Automatic fallback to heuristic if primary provider fails

**Quick Start:**
```powershell
python .\benchmarks\evaluator\judge.py
```

**Configuration:**
The judge automatically reads from `config/common.yaml`. Ensure these sections are configured:

```yaml
python_api:
  port: 8000

dotnet_api:
  urls: "http://localhost:5000"

llm_provider:
  provider: "ollama"           # or "openai" or "heuristic"
  model: "llama3:8b"
  ollama:
    base_url: "http://localhost:11434"
  openai:
    api_key: ""                # or use OPENAI_API_KEY env var
```

**Output:**
- `benchmarks/results/evaluation_report.md` - Human-readable comparison report
- `benchmarks/results/evaluation_results.json` - Detailed scores and comments

### Performance Tests (K6)

**Quick Start:**
```powershell
# Windows - Run all benchmarks
.\benchmarks\run-benchmarks.ps1 both

# Linux/macOS - Run all benchmarks  
./benchmarks/run-benchmarks.sh both
```

**What's Included:**
- **K6 Performance Tests**: Smoke, load, and stress testing
- **Cross-platform scripts**: PowerShell (Windows) and Bash (Linux/macOS)

**Prerequisites:**
- **K6**: `winget install k6` (Windows) or `brew install k6` (macOS)

📖 **Full documentation**: See [`benchmarks/README.md`](benchmarks/README.md) for detailed instructions and configuration options.

## Development Philosophy

This project follows **KISS principles** for microservices - simple, focused, and maintainable code without over-engineering. Each service has a single responsibility and minimal dependencies.

---

**Status**: � All core services functional - Ready for benchmarking