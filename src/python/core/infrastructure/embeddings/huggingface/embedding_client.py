from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from ....application.protocols.embeddings_protocol import EmbeddingsClient as EmbeddingsClientProtocol
from ...shared.config_loader import get_config

CONFIG_EMBEDDINGS_SERVICE = "embeddings_service"
CONFIG_MODEL_NAME = "model_name"
CONFIG_DEVICE = "device"
CONFIG_NORMALIZE = "normalize"

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_DEVICE = "cpu"
DEFAULT_NORMALIZE = True


class HuggingFaceEmbeddingsClient:
    def __init__(self, model_name: str = None, normalize: bool = None):
        cfg = get_config()
        embeddings_config = cfg.raw.get(CONFIG_EMBEDDINGS_SERVICE, {})
        
        self.model_name = model_name or embeddings_config.get(CONFIG_MODEL_NAME, DEFAULT_MODEL_NAME)
        self.normalize = normalize if normalize is not None else embeddings_config.get(CONFIG_NORMALIZE, DEFAULT_NORMALIZE)
        
        self._embeddings = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={"device": DEFAULT_DEVICE},
            encode_kwargs={"normalize_embeddings": self.normalize}
        )
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embeddings.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        return self._embeddings.embed_query(text)


def load_embeddings():
    from ..http_embeddings_client import HttpEmbeddingsClient
    from ...shared.config_loader import get_config
    
    cfg = get_config()
    return HttpEmbeddingsClient(base_url=cfg.get_embeddings_base_url())
