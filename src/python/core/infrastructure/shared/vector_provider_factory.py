from typing import Dict, Type
from ..vectorstores.chroma.chroma_vector_store import ChromaVectorStore
from ..vectorstores.qdrant.qdrant_vector_store import QdrantVectorStore
from ...application.protocols.vector_provider_protocol import VectorProvider
from ...domain.enums.vector_provider_type import VectorProviderType
from .config_loader import get_config

CONFIG_VECTOR_STORAGE = "vector_storage"
CONFIG_TYPE = "type"

PROVIDER_NATIVE = "native"
PROVIDER_QDRANT = "qdrant"


class VectorProviderFactory:
    _providers: Dict[VectorProviderType, Type[VectorProvider]] = {
        VectorProviderType.NATIVE: ChromaVectorStore,
        VectorProviderType.QDRANT: QdrantVectorStore,
    }
    
    @classmethod
    def create_provider(cls, provider_type: VectorProviderType = None) -> VectorProvider:
        if provider_type is None:
            cfg = get_config()
            conf_value = cfg.get_vector_storage_type()
            mapped = {
                PROVIDER_NATIVE: "NATIVE",
                PROVIDER_QDRANT: "QDRANT",
            }.get(conf_value.lower(), "NATIVE")
            provider_type = VectorProviderType.from_string(mapped)
        
        if provider_type not in cls._providers:
            available = [p.value for p in cls._providers.keys()]
            raise ValueError(f"Unknown vector provider: {provider_type.value}. Available: {available}")
        
        provider_class = cls._providers[provider_type]
        return provider_class()
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        return [provider_type.value for provider_type in cls._providers.keys()]
    
    @classmethod
    def register_provider(cls, provider_type: VectorProviderType, provider_class: Type[VectorProvider]):
        cls._providers[provider_type] = provider_class
