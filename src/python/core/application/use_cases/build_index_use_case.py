from typing import List
from ..dtos.index_info import IndexInfo
from ..protocols.embeddings_protocol import EmbeddingsClient
from ..protocols.vector_store_protocol import VectorStore
from ...domain.entities.candidate import CandidateRecord

TYPE_KEY = "type"
TYPE_CANDIDATE = "candidate"
CANDIDATE_ID_KEY = "candidate_id"
PREPARED_KEY = "prepared"
ENGLISH_LEVEL_KEY = "english_level"
ENGLISH_LEVEL_NUM_KEY = "english_level_num"
PROVIDER_LANGCHAIN = "LangChain"
ENGLISH_LEVEL_MAP = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}


class BuildIndexUseCase:
    def __init__(
        self, 
        embeddings_client: EmbeddingsClient, 
        vector_store: VectorStore
    ):
        self.embeddings_client = embeddings_client
        self.vector_store = vector_store
    
    async def execute(self, candidates: List[CandidateRecord]) -> IndexInfo:
        documents = []
        metadata = []
        
        for candidate in candidates:
            text_blocks = candidate.to_text_blocks()
            
            for block in text_blocks:
                documents.append(block)
                metadata.append({
                    TYPE_KEY: TYPE_CANDIDATE,
                    CANDIDATE_ID_KEY: candidate.candidate_id,
                    PREPARED_KEY: candidate.prepared,
                    ENGLISH_LEVEL_KEY: candidate.english_level,
                    ENGLISH_LEVEL_NUM_KEY: self._english_level_to_num(candidate.english_level),
                })
        
        embeddings = self.embeddings_client.embed_documents(documents)
        self.vector_store.add_documents(documents, embeddings, metadata)
        total_points = self.vector_store.count()
        
        return IndexInfo(
            candidates=len(candidates),
            chunks=len(documents),
            points=total_points,
            provider=PROVIDER_LANGCHAIN
        )
    
    def _english_level_to_num(self, level: str) -> int:
        return ENGLISH_LEVEL_MAP.get(level.upper(), 0)
