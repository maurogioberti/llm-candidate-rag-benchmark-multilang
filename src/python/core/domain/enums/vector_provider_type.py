from enum import Enum


class VectorProviderType(Enum):
    NATIVE = "NATIVE"
    QDRANT = "QDRANT"

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