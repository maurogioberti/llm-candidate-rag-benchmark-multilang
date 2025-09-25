from typing import Protocol, List, Dict, Any
from langchain_core.documents import Document


class VectorProvider(Protocol):
    def get_provider_name(self) -> str:
        ...
    
    def index_documents(self, documents: List[Document]) -> Dict[str, Any]:
        ...
