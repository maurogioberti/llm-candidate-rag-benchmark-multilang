import requests
from typing import List, Dict, Any, Tuple
from ...application.protocols.embeddings_protocol import EmbeddingsClient

ENDPOINT_EMBED = "/embed"
ENDPOINT_INSTRUCTION_PAIRS = "/instruction-pairs"
RESPONSE_VECTORS_KEY = "vectors"
RESPONSE_PAIRS_KEY = "pairs"
RESPONSE_TEXT_KEY = "text"
RESPONSE_METADATA_KEY = "metadata"


class HttpEmbeddingsWrapper:
    def __init__(self, http_client):
        self.http_client = http_client
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.http_client.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        return self.http_client.embed_query(text)


class HttpEmbeddingsClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self._embeddings = HttpEmbeddingsWrapper(self)
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = requests.post(
            f"{self.base_url}{ENDPOINT_EMBED}",
            json={"texts": texts}
        )
        response.raise_for_status()
        return response.json()[RESPONSE_VECTORS_KEY]
    
    def embed_query(self, text: str) -> List[float]:
        vectors = self.embed_documents([text])
        embedding = vectors[0]
        return embedding
    
    def get_instruction_pairs(self, path: str = None) -> List[Tuple[str, Dict[str, Any]]]:
        url = f"{self.base_url}{ENDPOINT_INSTRUCTION_PAIRS}"
        if path:
            url = f"{url}?path={path}"
            
        response = requests.get(url)
        response.raise_for_status()
        
        pairs_data = response.json()[RESPONSE_PAIRS_KEY]
        return [(pair[RESPONSE_TEXT_KEY], pair[RESPONSE_METADATA_KEY]) for pair in pairs_data]