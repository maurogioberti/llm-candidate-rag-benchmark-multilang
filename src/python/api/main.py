from pathlib import Path
from fastapi import FastAPI, HTTPException
from core.application.dtos.chat_request_dto import ChatRequestDto
from core.application.dtos.chat_result import ChatResult
from core.application.dtos.index_info import IndexInfo
from core.application.use_cases.ask_question_use_case import AskQuestionUseCase
from core.application.use_cases.build_index_use_case import BuildIndexUseCase
from core.application.services.candidate_service import CandidateService
from core.infrastructure.embeddings.http_embeddings_client import HttpEmbeddingsClient
from core.infrastructure.shared.vector_provider_factory import VectorProviderFactory
from core.infrastructure.llm.llm_factory import create_llm_client
from core.infrastructure.shared.config_loader import get_config

APP_TITLE = "Candidate RAG (LangChain)"
ROUTE_HEALTH = "/health"
ROUTE_INDEX = "/index"
ROUTE_CHAT = "/chat"
STATUS_OK = "ok"
ERROR_PREFIX = "LLM/Index error: "
INPUT_SUBDIR = "input"

cfg = get_config()

app = FastAPI(title=APP_TITLE)

embeddings_client = HttpEmbeddingsClient(base_url=cfg.get_embeddings_base_url())
vector_store = VectorProviderFactory.create_provider()
llm_client = create_llm_client()
candidate_service = CandidateService()

ask_question_use_case = AskQuestionUseCase(embeddings_client, vector_store, llm_client)
build_index_use_case = BuildIndexUseCase(embeddings_client, vector_store)


@app.get(ROUTE_HEALTH)
def health():
    return {"status": STATUS_OK}


@app.post(ROUTE_INDEX)
async def index():
    try:
        data_dir = cfg.get_data_root()
        input_dir = data_dir / INPUT_SUBDIR
        
        candidates = candidate_service.load_candidates_from_directory(input_dir)
        info = await build_index_use_case.execute(candidates)
        
        result = {"indexed": info.dict()}
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{ERROR_PREFIX}{e}")


@app.post(ROUTE_CHAT, response_model=ChatResult)
async def chat(req: ChatRequestDto):
    try:
        result = await ask_question_use_case.execute(req)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"{ERROR_PREFIX}{e}")
