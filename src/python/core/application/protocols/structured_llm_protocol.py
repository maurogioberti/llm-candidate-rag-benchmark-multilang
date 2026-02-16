"""Protocol for structured LLM clients that return typed objects."""

from typing import Protocol, TypeVar, Generic
from dataclasses import dataclass


T = TypeVar('T')


@dataclass
class ChatContext:
    """Context for structured LLM generation."""
    system_prompt: str
    user_message: str
    context: str | None = None


class StructuredLlmClient(Protocol, Generic[T]):
    """
    Protocol for LLM clients that return structured, typed outputs.
    
    Infrastructure layer handles:
    - JSON extraction and cleaning
    - Deserialization to type T
    - Retry with corrective prompts
    - Validation errors
    """
    
    async def generate_structured(self, chat_context: ChatContext) -> T:
        """
        Generate a structured response of type T from the LLM.
        
        Args:
            chat_context: Prompt context
            
        Returns:
            Deserialized object of type T
            
        Raises:
            LlmOutputValidationError: If output cannot be parsed
        """
        ...
