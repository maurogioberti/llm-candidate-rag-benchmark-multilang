from typing import List, Dict, Any
from langchain_core.documents import Document
from ....application.protocols.vector_provider_protocol import VectorProvider

PROVIDER_QDRANT = "QDRANT"


class QdrantVectorStore:
    def get_provider_name(self) -> str:
        return PROVIDER_QDRANT
    
    def index_documents(self, docs: List[Document]) -> Dict[str, Any]:
        from .qdrant_rest import QdrantREST
        from .qdrant_utils import index_documents_with_qdrant
        from ...embeddings.huggingface.embedding_client import load_embeddings
        
        qdrant = QdrantREST()
        embeddings = load_embeddings()
        total = index_documents_with_qdrant(docs, embeddings, qdrant)
        return {
            "chunks": len(docs),
            "points": total,
            "provider": self.get_provider_name()
        }
