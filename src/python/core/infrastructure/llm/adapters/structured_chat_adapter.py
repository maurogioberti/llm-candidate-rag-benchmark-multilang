"""Adapter that wraps LangChain BaseChatModel to provide structured output."""

import json
import logging
from typing import TypeVar, Generic, Type
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel

from core.application.protocols.structured_llm_protocol import ChatContext
from core.infrastructure.llm.exceptions.llm_output_validation_error import LlmOutputValidationError
from core.infrastructure.llm.extraction.llm_output_extractor import extract_json


T = TypeVar('T', bound=BaseModel)

logger = logging.getLogger(__name__)


class StructuredChatAdapter(Generic[T]):
    """
    Infrastructure adapter that wraps a LangChain chat model and provides
    structured, typed outputs with automatic retry and JSON extraction.
    """
    
    RETRY_USER_PROMPT = "Your previous response was not valid JSON. Respond ONLY with the valid JSON object. No markdown, no explanation."
    MAX_ATTEMPTS = 2
    
    def __init__(self, chat_model: BaseChatModel, output_type: Type[T]):
        """
        Args:
            chat_model: LangChain BaseChatModel (e.g., ChatOllama, ChatOpenAI)
            output_type: Pydantic model class to deserialize into
        """
        self.chat_model = chat_model
        self.output_type = output_type
    
    async def generate_structured(self, chat_context: ChatContext) -> T:
        """
        Generate structured output with retry on failure.
        
        Args:
            chat_context: Prompt context
            
        Returns:
            Deserialized Pydantic model of type T
            
        Raises:
            LlmOutputValidationError: If parsing fails after all retries
        """
        messages = self._build_messages(chat_context)
        last_raw_output = None
        
        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            response = await self.chat_model.ainvoke(messages)
            last_raw_output = response.content
            
            if not last_raw_output or not last_raw_output.strip():
                logger.warning(
                    f"Chat model returned empty response on attempt {attempt}/{self.MAX_ATTEMPTS}"
                )
            
            result = self._try_parse_output(last_raw_output, attempt)
            if result is not None:
                return result
            
            messages.append(AIMessage(content=last_raw_output))
            messages.append(HumanMessage(content=self.RETRY_USER_PROMPT))
        
        raise LlmOutputValidationError(
            f"Failed to extract valid {self.output_type.__name__} from LLM output after {self.MAX_ATTEMPTS} attempts",
            last_raw_output
        )
    
    def _try_parse_output(self, raw_output: str, attempt: int) -> T | None:
        """Attempt to parse raw output into typed model."""
        try:
            json_str = extract_json(raw_output)
            data = json.loads(json_str)
            return self.output_type(**data)
        except (ValueError, json.JSONDecodeError, Exception) as ex:
            logger.warning(
                f"Failed to parse structured output on attempt {attempt}/{self.MAX_ATTEMPTS} "
                f"for type {self.output_type.__name__}: {ex}"
            )
            return None
    
    def _build_messages(self, context: ChatContext) -> list:
        """Build LangChain message list from context."""
        messages = [SystemMessage(content=context.system_prompt)]
        
        if context.context:
            messages.append(SystemMessage(content=context.context))
        
        messages.append(HumanMessage(content=context.user_message))
        return messages
