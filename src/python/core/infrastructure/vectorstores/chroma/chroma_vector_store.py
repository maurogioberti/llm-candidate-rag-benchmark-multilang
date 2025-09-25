from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from ....application.protocols.vector_provider_protocol import VectorProvider
from ....application.protocols.vector_store_protocol import VectorStore

PROVIDER_NATIVE = "NATIVE"
DEFAULT_K = 4
DEFAULT_LIMIT = 6
DEFAULT_QUERY = "search query"


class ChromaVectorStore:
    def __init__(self):
        self._chroma_vectorstore = None
    
    def get_provider_name(self) -> str:
        return PROVIDER_NATIVE
    
    def index_documents(self, docs: List[Document]) -> Dict[str, Any]:
        from .chroma_utils import index_documents_with_chroma
        result = index_documents_with_chroma(docs)
        
        self._chroma_vectorstore = result.get("vectorstore")
        
        return {
            "chunks": len(docs),
            "provider": self.get_provider_name(),
            **result
        }
    
    def add_documents(self, documents: List[str], embeddings: List[List[float]] = None, metadata: List[Dict[str, Any]] = None) -> List[str]:
        if not self._chroma_vectorstore:
            self._ensure_vectorstore()
        
        from langchain_core.documents import Document
        langchain_docs = []
        
        for i, doc_text in enumerate(documents):
            doc_metadata = metadata[i] if metadata and i < len(metadata) else {}
            langchain_docs.append(Document(page_content=doc_text, metadata=doc_metadata))
        
        result = self._chroma_vectorstore.add_documents(langchain_docs)
        return result
    
    def similarity_search(
        self, 
        query: str, 
        k: int = DEFAULT_K,
        filter: Dict[str, Any] = None
    ) -> List[Document]:
        if not self._chroma_vectorstore:
            self._ensure_vectorstore()
        return self._chroma_vectorstore.similarity_search(query, k=k, filter=filter)
    
    def similarity_search_with_score(
        self, 
        query: str, 
        k: int = DEFAULT_K,
        filter: Dict[str, Any] = None
    ) -> List[tuple[Document, float]]:
        if not self._chroma_vectorstore:
            self._ensure_vectorstore()
        return self._chroma_vectorstore.similarity_search_with_score(query, k=k, filter=filter)
    
    def search(
        self,
        query_embedding: List[float],
        limit: int = DEFAULT_LIMIT,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[tuple[str, Dict[str, Any], float]]:
        if not self._chroma_vectorstore:
            self._ensure_vectorstore()
        
        try:
            if hasattr(self._chroma_vectorstore, 'similarity_search_by_vector_with_score'):
                results = self._chroma_vectorstore.similarity_search_by_vector_with_score(
                    query_embedding, k=limit, filter=filter_metadata
                )
            else:
                results = self._chroma_vectorstore.similarity_search_with_score(
                    DEFAULT_QUERY, k=limit, filter=filter_metadata
                )
        except Exception as e:
            results = []
        
        formatted_results = []
        for doc, score in results:
            formatted_results.append((doc.page_content, doc.metadata, score))
        
        return formatted_results
    
    def count(self) -> int:
        if not self._chroma_vectorstore:
            self._ensure_vectorstore()
        
        try:
            collection = self._chroma_vectorstore._collection
            count = collection.count()
            return count
        except Exception as e:
            return 0
    
    def _ensure_vectorstore(self):
        from .chroma_utils import load_existing_chroma
        if not self._chroma_vectorstore:
            self._chroma_vectorstore = load_existing_chroma()
