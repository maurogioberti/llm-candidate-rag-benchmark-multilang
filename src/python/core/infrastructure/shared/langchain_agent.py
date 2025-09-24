from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from ..embeddings.huggingface.embedding_client import load_embeddings
from ..vector_store import chroma_persistent
from .prompt_loader import load_prompt
from .config_loader import get_config

CONFIG_LLM_PROVIDER = "llm_provider"
CONFIG_PROVIDER = "provider"
CONFIG_MODEL = "model"
CONFIG_OLLAMA = "ollama"
CONFIG_OPENAI = "openai"
CONFIG_API_KEY = "api_key"
CONFIG_BASE_URL = "base_url"

PROVIDER_OLLAMA = "ollama"
PROVIDER_OPENAI = "openai"

PROMPT_SYSTEM_FILE = "chat_system.txt"
PROMPT_HUMAN_FILE = "chat_human.txt"
RETRIEVER_TOP_K = 6
TEMPERATURE_ZERO = 0
DEFAULT_RETRIEVAL_TYPES = "candidate"

ROLE_SYSTEM = "system"
ROLE_HUMAN = "human"

def _load_llm():
    cfg = get_config()
    llm_config = cfg.raw[CONFIG_LLM_PROVIDER]
    
    provider = llm_config[CONFIG_PROVIDER].lower()
    model_name = llm_config[CONFIG_MODEL]
    
    if provider == PROVIDER_OLLAMA:
        ollama_config = llm_config[CONFIG_OLLAMA]
        base_url = ollama_config[CONFIG_BASE_URL]
        return ChatOllama(model=model_name, base_url=base_url, temperature=TEMPERATURE_ZERO)
    
    elif provider == PROVIDER_OPENAI:
        openai_config = llm_config[CONFIG_OPENAI]
        base_url = openai_config[CONFIG_BASE_URL]
        api_key = openai_config[CONFIG_API_KEY]
        
        if not api_key:
            raise RuntimeError("Missing OpenAI API key in configuration")
        
        return ChatOpenAI(model=model_name, base_url=base_url, api_key=api_key, temperature=TEMPERATURE_ZERO)
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}. Supported: {PROVIDER_OLLAMA}, {PROVIDER_OPENAI}")

def build_chain():
    embeddings = load_embeddings()
    vector_store = chroma_persistent(embeddings)
    types = DEFAULT_RETRIEVAL_TYPES
    metadata_filter = {"type": {"$in": [t.strip() for t in types.split(",") if t.strip()]}}
    retriever = vector_store.as_retriever(search_kwargs={"k": RETRIEVER_TOP_K, "filter": metadata_filter})
    system_prompt = load_prompt(PROMPT_SYSTEM_FILE)
    human_prompt = load_prompt(PROMPT_HUMAN_FILE)
    prompt = ChatPromptTemplate.from_messages([
        (ROLE_SYSTEM, system_prompt),
        (ROLE_HUMAN, human_prompt),
    ])
    llm = _load_llm()
    doc_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, doc_chain)

def build_index():
    return build_chain()
