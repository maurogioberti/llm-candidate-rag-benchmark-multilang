"""
LLM Client Factory

Creates and configures LangChain chat models based on application configuration.
Exposes LangChain's BaseChatModel directly as the core abstraction.

This module owns:
- Provider selection logic
- Configuration validation
- Client instantiation

It does NOT wrap LangChain - consumers use BaseChatModel directly.
"""

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from ..shared.config_loader import get_config


PROVIDER_OLLAMA = "ollama"
PROVIDER_OPENAI = "openai"
DEFAULT_TEMPERATURE = 0.0


def create_llm_client() -> BaseChatModel:
    """
    Creates and configures an LLM client based on application configuration.
    
    Returns:
        BaseChatModel: A configured LangChain chat model instance.
        
    Raises:
        RuntimeError: If OpenAI API key is missing when using OpenAI provider.
        ValueError: If the configured provider is not supported.
    """
    cfg = get_config()
    llm_config = cfg.raw["llm_provider"]
    
    provider = llm_config["provider"].lower()
    model_name = llm_config["model"]
    
    if provider == PROVIDER_OLLAMA:
        base_url = llm_config["ollama"]["base_url"]
        return ChatOllama(
            model=model_name,
            base_url=base_url,
            temperature=DEFAULT_TEMPERATURE
        )
    
    elif provider == PROVIDER_OPENAI:
        openai_config = llm_config["openai"]
        base_url = openai_config["base_url"]
        api_key = openai_config["api_key"]
        
        if not api_key:
            raise RuntimeError("Missing OpenAI API key in configuration")
        
        return ChatOpenAI(
            model=model_name,
            base_url=base_url,
            api_key=api_key,
            temperature=DEFAULT_TEMPERATURE
        )
    
    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}. "
            f"Supported: {PROVIDER_OLLAMA}, {PROVIDER_OPENAI}"
        )
