from typing import List
from ..dtos.chat_request_dto import ChatRequestDto
from ..dtos.chat_result import ChatResult, ChatSource
from ..protocols.embeddings_protocol import EmbeddingsClient
from ..protocols.vector_store_protocol import VectorStore
from ..protocols.llm_protocol import LlmClient
from ...infrastructure.shared.config_loader import get_config
from ...infrastructure.shared.prompt_loader import load_prompt

DEFAULT_LIMIT = 6
PREPARED_KEY = "prepared"
ENGLISH_LEVEL_NUM_MIN_KEY = "english_level_num_min"
CANDIDATE_ID_KEY = "candidate_id"
IN_OPERATOR = "$in"
CONTEXT_SEPARATOR = "\n\n"
UNKNOWN_VALUE = "unknown"
TYPE_KEY = "type"
DEFAULT_CONTENT_LIMIT = 200
CONTENT_SUFFIX = "..."
CHAT_SYSTEM_FILE = "chat_system.md"
CHAT_HUMAN_FILE = "chat_human.md"
ENGLISH_LEVEL_MAP = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}


class AskQuestionUseCase:
    def __init__(
        self, 
        embeddings_client: EmbeddingsClient, 
        vector_store: VectorStore, 
        llm_client: LlmClient
    ):
        self.embeddings_client = embeddings_client
        self.vector_store = vector_store
        self.llm_client = llm_client
    
    async def execute(self, request: ChatRequestDto) -> ChatResult:
        query_embedding = self.embeddings_client.embed_query(request.question)
        metadata_filter = self._build_metadata_filter(request.filters)
        
        search_results = self.vector_store.search(
            query_embedding=query_embedding,
            limit=DEFAULT_LIMIT,
            filter_metadata=metadata_filter
        )
        
        if not search_results:
            return ChatResult(
                answer="No candidates found matching the specified criteria.",
                sources=[]
            )
        
        context = self._build_context(search_results)
        sources = self._extract_sources(search_results)
        
        human_prompt = self._get_human_prompt(context, request.question)
        system_prompt = self._get_system_prompt()
        
        answer = self.llm_client.generate_chat_completion(
            system_prompt=system_prompt,
            user_message=human_prompt,
            context=context
        )
        
        return ChatResult(
            answer=answer,
            sources=sources
        )
    
    def _build_metadata_filter(self, filters):
        if not filters:
            return None
            
        conditions = []
        
        if filters.prepared is not None:
            conditions.append({PREPARED_KEY: filters.prepared})
            
        if filters.english_min:
            conditions.append({ENGLISH_LEVEL_NUM_MIN_KEY: ENGLISH_LEVEL_MAP.get(filters.english_min.upper(), 0)})
            
        if filters.candidate_ids:
            conditions.append({CANDIDATE_ID_KEY: {"$in": filters.candidate_ids}})
        
        if not conditions:
            return None
        
        if len(conditions) == 1:
            return conditions[0]
        
        # For multiple conditions, Chroma expects them to be combined with $and
        return {"$and": conditions}
    
    def _build_context(self, search_results: List) -> str:
        context_parts = []
        for document, metadata, score in search_results:
            context_parts.append(document)
        return CONTEXT_SEPARATOR.join(context_parts)
    
    def _extract_sources(self, search_results: List) -> List[ChatSource]:
        sources = []
        for document, metadata, score in search_results:
            sources.append(ChatSource(
                candidate_id=metadata.get(CANDIDATE_ID_KEY, UNKNOWN_VALUE),
                section=metadata.get(TYPE_KEY, UNKNOWN_VALUE),
                content=document[:DEFAULT_CONTENT_LIMIT] + CONTENT_SUFFIX if len(document) > DEFAULT_CONTENT_LIMIT else document,
                score=score
            ))
        return sources
    
    def _get_system_prompt(self) -> str:
        return load_prompt(CHAT_SYSTEM_FILE)
    
    def _get_human_prompt(self, context: str, question: str) -> str:
        human_template = load_prompt(CHAT_HUMAN_FILE)
        return human_template.format(context=context, input=question)
