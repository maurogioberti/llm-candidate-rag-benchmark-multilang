# LLM Candidate RAG Benchmark - Multi-Language

A benchmarking project to compare RAG (Retrieval-Augmented Generation) implementations for candidate matching using two different tech stacks:

- **Python** with LangChain framework
- **C#** with Semantic Kernel framework

## Current Implementation Status

🟢 **Embeddings Service** - Ready  
🔶 **Python API** - Coming Soon  
🔶 **C# API** - Coming Soon  

## Architecture Overview

```
llm-candidate-rag-benchmark-multilang/
├── data/
│   └── instructions/           # Training/evaluation datasets
│       └── embedings.jsonl     # Candidate matching examples
├── services/
│   └── embeddings-python/      # Shared embeddings microservice
├── config/
│   └── common.yaml            # Centralized configuration
└── ... (more components coming)
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

2. **Start the embeddings service:**
   ```bash
   py -m services.embeddings-python.run_server
   ```

   The service will start on the host/port configured in `config/common.yaml` under `EmbeddingsService` section.

### Configuration

The service reads configuration from `config/common.yaml`. Required sections:

```yaml
EmbeddingsService:
  Host: "0.0.0.0"
  Port: 8080
  InstructionFile: "embeddings.jsonl"

Data:
  Root: "./data"
  EmbInstructions: "instructions"
```

## Dataset Format

The instruction pairs follow this JSONL format:

```json
{
  "query": "Tech Lead backend with C1 English and mentoring experience",
  "positive": "MauroGiobertiBackendDotNetEnglishC1TechLead|GeneralInfo: 12 years, Tech Lead, mentoring, English C1",
  "negative": "JeronimoGarciaFrontendReactEnglishB2|Experience: 3 years React/Next.js, migration AngularJS→Next.js"
}
```

Each line contains:
- **query**: Job requirement or search criteria
- **positive**: Matching candidate profile  
- **negative**: Non-matching candidate profile

## What's Coming Next

- **Python RAG API** using LangChain
- **C# RAG API** using Semantic Kernel  
- **Performance comparison** between both implementations
- **Docker infrastructure** for easy deployment
- **Cross-platform scripts** for running all services

## Development Philosophy

This project follows **KISS principles** for microservices - simple, focused, and maintainable code without over-engineering. Each service has a single responsibility and minimal dependencies.

---

**Status**: 🚧 Early Development - Embeddings service functional, APIs in progress