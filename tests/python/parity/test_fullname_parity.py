"""
Integration test: Verify Python returns real human fullname (not candidate_id).
This ensures Python/NET parity.
"""
import sys
import asyncio
sys.path.insert(0, 'src/python')

from core.application.dtos.chat_request_dto import ChatRequestDto
from core.application.use_cases.ask_question_use_case import AskQuestionUseCase
from core.application.use_cases.build_vector_index_use_case import build_index
from core.infrastructure.embeddings.http_embeddings_client import HttpEmbeddingsClient
from core.infrastructure.shared.vector_provider_factory import VectorProviderFactory
from core.infrastructure.llm.openai.llm_client import OpenAILlmClient
from core.infrastructure.shared.config_loader import get_config

TEST_QUERY_JAVA = "who is the best candidate for java?"
EXPECTED_JAVA_CANDIDATE_FULLNAME = "Jan-Claudiu Crisan"

print("Building index...")
info = build_index()
print(f"Indexed {info['chunks']} chunks\n")

cfg = get_config()
embeddings_client = HttpEmbeddingsClient(base_url=cfg.get_embeddings_base_url())
vector_store = VectorProviderFactory.create_provider()
llm_client = OpenAILlmClient()

use_case = AskQuestionUseCase(embeddings_client, vector_store, llm_client)

print(f"Testing query: '{TEST_QUERY_JAVA}'")
request = ChatRequestDto(question=TEST_QUERY_JAVA)

async def test():
    result = await use_case.execute(request)
    return result

result = asyncio.run(test())

print("\nMetadata:")
print(f"  selected_candidate: {result.metadata.get('selected_candidate', {})}")

actual_fullname = result.metadata.get('selected_candidate', {}).get('fullname', 'MISSING')

print(f"\n{'='*70}")
if actual_fullname == EXPECTED_JAVA_CANDIDATE_FULLNAME:
    print(f"PASS: Fullname is correct: '{actual_fullname}'")
    print("Python/NET parity achieved!")
else:
    print(f"FAIL: Expected '{EXPECTED_JAVA_CANDIDATE_FULLNAME}', got '{actual_fullname}'")
    sys.exit(1)
print(f"{'='*70}")

assert result.metadata["selected_candidate"]["fullname"] == EXPECTED_JAVA_CANDIDATE_FULLNAME, \
    f"Expected fullname='{EXPECTED_JAVA_CANDIDATE_FULLNAME}', got '{actual_fullname}'"

print("\nAll assertions passed!")
