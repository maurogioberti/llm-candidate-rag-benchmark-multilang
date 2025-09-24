from enum import Enum

PROVIDER_NATIVE = "NATIVE"
PROVIDER_QDRANT = "QDRANT"
DEFAULT_PROVIDER = PROVIDER_QDRANT

class VectorProviderType(Enum):
    NATIVE = PROVIDER_NATIVE
    QDRANT = PROVIDER_QDRANT

    @classmethod
    def from_string(cls, value: str) -> 'VectorProviderType':
        if not value:
            return cls.QDRANT
        
        value = value.upper().strip()
        for provider in cls:
            if provider.value == value:
                return provider
        
        return cls.QDRANT

    @classmethod
    def get_available_types(cls) -> list[str]:
        return [provider.value for provider in cls]