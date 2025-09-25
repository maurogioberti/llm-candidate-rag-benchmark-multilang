from typing import List, Dict
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from ....application.protocols.llm_protocol import LlmClient as LlmClientProtocol
from ...shared.config_loader import get_config


CONFIG_LLM_PROVIDER = "llm_provider"
CONFIG_PROVIDER = "provider"
CONFIG_MODEL = "model"
CONFIG_OLLAMA = "ollama"
CONFIG_OPENAI = "openai"
CONFIG_API_KEY = "api_key"
CONFIG_BASE_URL = "base_url"

PROVIDER_OLLAMA = "ollama"
PROVIDER_OPENAI = "openai"

ROLE_SYSTEM = "system"
ROLE_USER = "user"
ROLE_HUMAN = "human"

EMPTY_STRING = ""
TEMPERATURE = 0.0

CONTEXT_TEMPLATE = "Context:\n{context}\n\nQuestion:\n{user_message}"


class OpenAILlmClient:
    def __init__(self):
        self._llm = self._create_llm()
    
    def _create_llm(self):
        cfg = get_config()
        llm_config = cfg.raw[CONFIG_LLM_PROVIDER]
        
        provider = llm_config[CONFIG_PROVIDER].lower()
        model_name = llm_config[CONFIG_MODEL]
        
        if provider == PROVIDER_OLLAMA:
            ollama_config = llm_config[CONFIG_OLLAMA]
            base_url = ollama_config[CONFIG_BASE_URL]
            return ChatOllama(model=model_name, base_url=base_url, temperature=TEMPERATURE)
        
        elif provider == PROVIDER_OPENAI:
            openai_config = llm_config[CONFIG_OPENAI]
            base_url = openai_config[CONFIG_BASE_URL]
            api_key = openai_config[CONFIG_API_KEY]
            
            if not api_key:
                raise RuntimeError("Missing OpenAI API key in configuration")
            
            return ChatOpenAI(
                model=model_name, 
                base_url=base_url, 
                api_key=api_key, 
                temperature=TEMPERATURE
            )
        
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}. Supported: {PROVIDER_OLLAMA}, {PROVIDER_OPENAI}")
    
    def generate_response(self, messages: List[Dict[str, str]], temperature: float = TEMPERATURE) -> str:
        langchain_messages = []
        
        for msg in messages:
            role = msg.get("role", ROLE_HUMAN)
            content = msg.get("content", EMPTY_STRING)
            
            if role == ROLE_SYSTEM:
                langchain_messages.append(SystemMessage(content=content))
            else:
                langchain_messages.append(HumanMessage(content=content))
        
        response = self._llm.invoke(langchain_messages)
        return response.content
    
    def generate_chat_completion(self, system_prompt: str, user_message: str, context: str = EMPTY_STRING) -> str:
        full_user_message = user_message
        if context:
            full_user_message = CONTEXT_TEMPLATE.format(context=context, user_message=user_message)
        
        messages = [
            {"role": ROLE_SYSTEM, "content": system_prompt},
            {"role": ROLE_USER, "content": full_user_message}
        ]
        
        try:
            response = self.generate_response(messages)
            return response
        except Exception as e:
            raise