from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from ....application.protocols.vector_provider_protocol import VectorProvider

PROVIDER_QDRANT = "QDRANT"
DEFAULT_LIMIT = 6


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
    
    def add_documents(self, documents: List[str], embeddings: List[List[float]] = None, metadata: List[Dict[str, Any]] = None) -> List[str]:
        from langchain_core.documents import Document
        langchain_docs = []
        
        for i, doc_text in enumerate(documents):
            doc_metadata = metadata[i] if metadata and i < len(metadata) else {}
            langchain_docs.append(Document(page_content=doc_text, metadata=doc_metadata))
        
        result = self.index_documents(langchain_docs)
        return [f"doc_{i}" for i in range(len(documents))]
    
    def search(
        self,
        query_embedding: List[float],
        limit: int = DEFAULT_LIMIT,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[tuple[str, Dict[str, Any], float]]:
        try:
            from .qdrant_rest import QdrantREST
            qdrant = QdrantREST()
            
            results = qdrant.search(
                collection="candidates",
                query_vector=query_embedding,
                limit=limit,
                qfilter=filter_metadata
            )
            
            formatted_results = []
            for result in results:
                payload = result.get("payload", {})
                content = payload.get("document", "")
                metadata = {k: v for k, v in payload.items() if k != "document"}
                score = result.get("score", 0.0)
                
                formatted_results.append((content, metadata, score))
            
            return formatted_results
            
        except Exception as e:
            return []
    
    def count(self) -> int:
        try:
            from .qdrant_rest import QdrantREST
            qdrant = QdrantREST()
            count = qdrant.count("candidates")
            return count
        except Exception as e:
            return 0
