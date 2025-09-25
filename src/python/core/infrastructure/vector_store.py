from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from langchain_chroma import Chroma
from langchain_core.documents import Document
from ..application.protocols.vector_store_protocol import VectorStore
from .shared.config_loader import get_config

CONFIG_DATA_ROOT = "root"
VECTORS_SUBDIR = "vectors"
CHROMA_SUBDIR = "chroma"

cfg = get_config()
BASE_VECTORS_DIR = cfg.get_data_root() / VECTORS_SUBDIR
BASE_VECTORS_DIR.mkdir(parents=True, exist_ok=True)


class ChromaVectorStore:
    def __init__(self, embeddings_client):
        self.embeddings_client = embeddings_client
        self._chroma = None
        self._init_chroma()
    
    def _init_chroma(self):
        persist_directory = str(BASE_VECTORS_DIR / CHROMA_SUBDIR)
        
        try:
            self._chroma = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings_client._embeddings
            )
        except:
            self._chroma = None
    
    def add_documents(self, documents: List[str], embeddings: List[List[float]], metadata: List[Dict[str, Any]]) -> None:
        docs = []
        for i, (text, meta) in enumerate(zip(documents, metadata)):
            docs.append(Document(page_content=text, metadata=meta))
        
        if self._chroma is None:
            persist_directory = str(BASE_VECTORS_DIR / CHROMA_SUBDIR)
            self._chroma = Chroma.from_documents(
                docs, 
                self.embeddings_client._embeddings, 
                persist_directory=persist_directory
            )
        else:
            self._chroma.add_documents(docs)
    
    def search(self, query_embedding: List[float], limit: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> List[Tuple[str, Dict[str, Any], float]]:
        if not self._chroma:
            return []
        
        try:
            results = self._chroma.similarity_search_with_score_by_vector(
                embedding=query_embedding,
                k=limit,
                filter=filter_metadata
            )
        except AttributeError:
            results = self._chroma.similarity_search_with_score(
                query="",
                k=limit,
                filter=filter_metadata
            )
        
        formatted_results = []
        for doc, score in results:
            formatted_results.append((
                doc.page_content,
                doc.metadata,
                float(score)
            ))
        
        return formatted_results
    
    def count(self) -> int:
        if not self._chroma:
            return 0
        
        try:
            collection = getattr(self._chroma, "_collection", None)
            if collection:
                return collection.count()
        except:
            pass
        
        return 0


def chroma_from_documents(docs: List[Document], embeddings):
    persist_directory = str(BASE_VECTORS_DIR / CHROMA_SUBDIR)
    return Chroma.from_documents(docs, embeddings, persist_directory=persist_directory)


def chroma_persistent(embeddings):
    persist_directory = str(BASE_VECTORS_DIR / CHROMA_SUBDIR)
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings)


def chroma_from_existing(embeddings):
    return chroma_persistent(embeddings)


def build_metadata_filter(prepared: bool | None = None, english_min: str | None = None) -> Dict[str, Any] | None:
    english_level_map = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}
    meta_prepared = "prepared"
    meta_english_level_min = "english_level_num_min"
    
    metadata: Dict[str, Any] = {}
    if prepared is not None:
        metadata[meta_prepared] = prepared
    if english_min:
        metadata[meta_english_level_min] = english_level_map.get(english_min.upper(), 0)
    return metadata or None
