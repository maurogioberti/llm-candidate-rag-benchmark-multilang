import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

import asyncio
from pathlib import Path
from core.application.use_cases.ask_question_use_case import AskQuestionUseCase
from core.application.use_cases.build_index_use_case import BuildIndexUseCase
from core.application.services.candidate_service import CandidateService
from core.application.dtos.chat_request_dto import ChatRequestDto
from core.infrastructure.embeddings.http_embeddings_client import HttpEmbeddingsClient
from core.infrastructure.shared.vector_provider_factory import VectorProviderFactory
from core.infrastructure.llm.openai.llm_client import OpenAILlmClient
from core.infrastructure.shared.config_loader import get_config

TEST_QUERY_JAVA = "who is the best candidate for java?"
EXPECTED_JAVA_CANDIDATE_FULLNAME = "Jan-Claudiu Crisan"
EXPECTED_CANDIDATE_ID_FRAGMENT = "JanClaudiuCrisan"


async def test_best_java_candidate_returns_human_fullname():
    """
    Test that querying for the best Java candidate returns:
    - Real human fullname (e.g., "Jan-Claudiu Crisan")
    - NOT the dataset slug (e.g., "JanClaudiuCrisanJavaBackendSpringEnglishC1")
    - fullname != candidate_id
    """
    cfg = get_config()
    
    embeddings_client = HttpEmbeddingsClient(base_url=cfg.get_embeddings_base_url())
    vector_store = VectorProviderFactory.create_provider()
    llm_client = OpenAILlmClient()
    candidate_service = CandidateService()
    
    data_dir = cfg.get_data_root()
    input_dir = data_dir / "input"
    
    candidates = candidate_service.load_candidates_from_directory(input_dir)
    
    build_index_use_case = BuildIndexUseCase(embeddings_client, vector_store)
    await build_index_use_case.execute(candidates)
    
    ask_question_use_case = AskQuestionUseCase(embeddings_client, vector_store, llm_client)
    
    request = ChatRequestDto(question=TEST_QUERY_JAVA)
    result = await ask_question_use_case.execute(request)
    
    assert result.metadata is not None, "Result metadata is None"
    assert result.metadata["selected_candidate"] is not None, "Selected candidate is None"
    
    fullname = result.metadata["selected_candidate"]["fullname"]
    candidate_id = result.metadata["selected_candidate"]["candidate_id"]
    
    print(f"[OK] Selected candidate fullname: {fullname}")
    print(f"[OK] Selected candidate ID: {candidate_id}")
    
    assert fullname == EXPECTED_JAVA_CANDIDATE_FULLNAME, f"Expected fullname '{EXPECTED_JAVA_CANDIDATE_FULLNAME}', got '{fullname}'"
    
    assert EXPECTED_CANDIDATE_ID_FRAGMENT in candidate_id, f"Expected candidate_id to contain '{EXPECTED_CANDIDATE_ID_FRAGMENT}', got '{candidate_id}'"
    
    assert fullname != candidate_id, f"FAIL: fullname should NOT equal candidate_id! Both are '{fullname}'"
    
    print("\n" + "="*80)
    print("[PASS] TEST PASSED")
    print("="*80)
    print(f"Selected Candidate: {fullname} (ID: {candidate_id}, Rank: 1)")
    print(f"fullname != candidate_id: {fullname} != {candidate_id}")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(test_best_java_candidate_returns_human_fullname())
