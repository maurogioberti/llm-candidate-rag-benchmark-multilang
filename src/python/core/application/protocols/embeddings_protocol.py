from typing import Protocol, List
from langchain_core.documents import Document


class EmbeddingsClient(Protocol):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        ...
    
    def embed_query(self, text: str) -> List[float]:
        ...