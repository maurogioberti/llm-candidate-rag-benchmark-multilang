from typing import Protocol, List, Dict, Any
from langchain_core.documents import Document


class VectorStore(Protocol):
    def add_documents(self, documents: List[Document]) -> List[str]:
        ...
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 4,
        filter: Dict[str, Any] = None
    ) -> List[Document]:
        ...
    
    def similarity_search_with_score(
        self, 
        query: str, 
        k: int = 4,
        filter: Dict[str, Any] = None
    ) -> List[tuple[Document, float]]:
        ...
