# LLM C## Current Implementation Status

🟢 **Embeddings Service** - Ready  
🟢 **Python API** - Ready  
🟢 **C# API** - Readyate RAG Benchmark - Multi-Language

A benchmarking project to compare RAG (Retrieval-Augmented Generation) implementations for candidate matching using two different tech stacks:

- **Python** with LangChain framework
- **C#** with Semantic Kernel framework

## Current Implementation Status

🟢 **Embeddings Service** - Ready  
🔶 **Python API** - Coming Soon  
� **C# API** - Ready  

## Architecture Overview

```
llm-candidate-rag-benchmark-multilang/
├── config/
│   └── common.yaml            # Centralized configuration
├── data/
│   ├── input/                 # Raw candidate data (JSON profiles)
│   ├── instructions/          # Training datasets
│   │   └── embedings.jsonl    # Synthetic candidate matching examples
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
│   └── python/                # Python RAG implementation (coming soon)
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
   
   **Opción 1: Desde la raíz del proyecto (recomendado)**
   ```bash
   python run_embeddings_server.py
   ```
   
   **Opción 2: Usando el módulo del servicio**
   ```bash
   python -m services.embeddings-python.run_embeddings_server
   ```

   The service will start on the host/port configured in `config/common.yaml` under `embeddings_service` section.

### Running the APIs

#### C# API (Semantic Kernel)

1. **Prerequisites:**
   - .NET 8.0+ SDK
   - Running embeddings service (see above)

2. **Start the C# API:**
   ```bash
   dotnet run --project src/dotnet/Rag.Candidates.Api.csproj
   ```

   The API will start on the host/port configured in `config/common.yaml` under `dotnet_api` section.

#### Python API (LangChain)

1. **Prerequisites:**
   - Python 3.10+ with virtual environment
   - Running embeddings service and vector database (Qdrant)
   - Installed dependencies (`pip install -e .`)

2. **Start the Python API:**
   ```bash
   python src/python/langchain_api.py serve
   ```

   The API will start on the host/port configured in `config/common.yaml` under `python_api` section.

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

**Embeddings Instructions (`embedings.jsonl`)**  
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

## What's Coming Next

- **Python RAG API** using LangChain
- **Performance comparison** between both implementations
- **Cross-platform scripts** for running all services

## Development Philosophy

This project follows **KISS principles** for microservices - simple, focused, and maintainable code without over-engineering. Each service has a single responsibility and minimal dependencies.

---

**Status**: � All core services functional - Ready for benchmarking