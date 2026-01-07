from typing import List
from ..dtos.chat_request_dto import ChatRequestDto
from ..dtos.chat_result import ChatResult, ChatSource
from ..protocols.embeddings_protocol import EmbeddingsClient
from ..protocols.vector_store_protocol import VectorStore
from ..protocols.llm_protocol import LlmClient
from ...domain.configuration.vector_metadata_config import DEFAULT_VECTOR_METADATA_CONFIG
from ...infrastructure.shared.config_loader import get_config
from ...infrastructure.shared.prompt_loader import load_prompt
from ..services.query_parser import QueryParser
from ..services.candidate_aggregator import CandidateAggregator
from ..services.metadata_filter_builder import MetadataFilterBuilder
from ..services.candidate_ranker import CandidateRanker
from ...domain.configuration.ranking_weights import RankingWeights
from ...domain.entities.llm_response_schema import LlmResponseSchema, SelectedCandidate
import json

METADATA_CONFIG = DEFAULT_VECTOR_METADATA_CONFIG

DEFAULT_LIMIT = 6
IN_OPERATOR = "$in"
CONTEXT_SEPARATOR = "\n\n"
UNKNOWN_VALUE = "unknown"
DEFAULT_CONTENT_LIMIT = 200
CONTENT_SUFFIX = "..."
CHAT_SYSTEM_FILE = "chat_system.md"
CHAT_HUMAN_FILE = "chat_human.md"
ENGLISH_LEVEL_MAP = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}

PREPARED_KEY = "prepared"
ENGLISH_LEVEL_NUM_MIN_KEY = "english_level_num_min"


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
        self.query_parser = QueryParser()
        self.candidate_aggregator = CandidateAggregator(METADATA_CONFIG.FIELD_CANDIDATE_ID)
        self.candidate_ranker = CandidateRanker(RankingWeights.default())
        self.filter_builder = MetadataFilterBuilder(
            candidate_id_field=METADATA_CONFIG.FIELD_CANDIDATE_ID,
            seniority_field=METADATA_CONFIG.FIELD_SENIORITY_LEVEL,
            years_experience_field=METADATA_CONFIG.FIELD_YEARS_EXPERIENCE,
            skill_name_field=METADATA_CONFIG.FIELD_SKILL_NAME,
            type_field=METADATA_CONFIG.FIELD_TYPE,
            type_skill=METADATA_CONFIG.TYPE_SKILL
        )
    
    async def execute(self, request: ChatRequestDto) -> ChatResult:
        parsed_query = self.query_parser.parse(request.question)
        
        query_embedding = self.embeddings_client.embed_query(request.question)
        metadata_filter = self._build_metadata_filter(request.filters, parsed_query)
        
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
        
        aggregated_candidates = self.candidate_aggregator.aggregate(search_results)
        filtered_candidates = self.filter_builder.filter_aggregated_candidates(
            aggregated_candidates,
            parsed_query
        )
        
        if not filtered_candidates:
            return ChatResult(
                answer="No candidates found matching the specified criteria.",
                sources=[]
            )
        
        ranked_candidates = self.candidate_ranker.rank(filtered_candidates, parsed_query)
        
        context = self._build_context_from_candidates(ranked_candidates)
        sources = self._extract_sources_from_candidates(ranked_candidates)
        
        human_prompt = self._get_human_prompt(context, request.question)
        system_prompt = self._get_system_prompt()
        
        llm_output = self.llm_client.generate_chat_completion(
            system_prompt=system_prompt,
            user_message=human_prompt,
            context=context
        )
        
        parsed_response = self._parse_and_validate_llm_output(llm_output)
        
        answer = self._format_final_answer(parsed_response)
        
        metadata = self._build_response_metadata(parsed_response)
        
        return ChatResult(
            answer=answer,
            sources=sources,
            metadata=metadata
        )
    
    def _build_metadata_filter(self, filters, parsed_query):
        conditions = []
        
        if filters:
            if filters.prepared is not None:
                conditions.append({PREPARED_KEY: filters.prepared})
                
            if filters.english_min:
                conditions.append({ENGLISH_LEVEL_NUM_MIN_KEY: ENGLISH_LEVEL_MAP.get(filters.english_min.upper(), 0)})
                
            if filters.candidate_ids:
                conditions.append({METADATA_CONFIG.FIELD_CANDIDATE_ID: {IN_OPERATOR: filters.candidate_ids}})
        
        query_filters = self.filter_builder.build_candidate_filters(parsed_query)
        conditions.extend(query_filters)
        
        tech_filter = self.filter_builder.build_technology_filters(parsed_query)
        if tech_filter:
            conditions.append(tech_filter)
        
        if not conditions:
            return None
        
        if len(conditions) == 1:
            return conditions[0]
        
        return {"$and": conditions}
    
    def _build_context_from_candidates(self, candidates: List) -> str:
        context_parts = []
        for candidate in candidates:
            for document in candidate.documents:
                context_parts.append(document)
        return CONTEXT_SEPARATOR.join(context_parts)
    
    def _extract_sources_from_candidates(self, candidates: List) -> List[ChatSource]:
        sources = []
        for candidate in candidates:
            for i, document in enumerate(candidate.documents):
                sources.append(ChatSource(
                    candidate_id=candidate.candidate_id,
                    section=candidate.metadata.get(METADATA_CONFIG.FIELD_TYPE, UNKNOWN_VALUE),
                    content=document[:DEFAULT_CONTENT_LIMIT] + CONTENT_SUFFIX if len(document) > DEFAULT_CONTENT_LIMIT else document,
                    score=candidate.all_scores[i] if i < len(candidate.all_scores) else 0.0
                ))
        return sources
    
    def _build_context(self, search_results: List) -> str:
        context_parts = []
        for document, metadata, score in search_results:
            context_parts.append(document)
        return CONTEXT_SEPARATOR.join(context_parts)
    
    def _extract_sources(self, search_results: List) -> List[ChatSource]:
        sources = []
        for document, metadata, score in search_results:
            sources.append(ChatSource(
                candidate_id=metadata.get(METADATA_CONFIG.FIELD_CANDIDATE_ID, UNKNOWN_VALUE),
                section=metadata.get(METADATA_CONFIG.FIELD_TYPE, UNKNOWN_VALUE),
                content=document[:DEFAULT_CONTENT_LIMIT] + CONTENT_SUFFIX if len(document) > DEFAULT_CONTENT_LIMIT else document,
                score=score
            ))
        return sources
    
    def _get_system_prompt(self) -> str:
        return load_prompt(CHAT_SYSTEM_FILE)
    
    def _get_human_prompt(self, context: str, question: str) -> str:
        human_template = load_prompt(CHAT_HUMAN_FILE)
        return human_template.format(context=context, input=question)
    
    def _parse_and_validate_llm_output(self, llm_output: str) -> LlmResponseSchema:
        try:
            json_start = llm_output.find('{')
            json_end = llm_output.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON object found in LLM output")
            
            json_str = llm_output[json_start:json_end]
            data = json.loads(json_str)
            
            if "justification" not in data:
                raise ValueError("Missing required field: justification")
            
            selected_candidate = None
            if data.get("selected_candidate") is not None:
                candidate_data = data["selected_candidate"]
                
                if "fullname" not in candidate_data or "candidate_id" not in candidate_data or "rank" not in candidate_data:
                    raise ValueError("selected_candidate must contain fullname, candidate_id, and rank")
                
                selected_candidate = SelectedCandidate(
                    fullname=candidate_data["fullname"],
                    candidate_id=candidate_data["candidate_id"],
                    rank=candidate_data["rank"]
                )
            
            return LlmResponseSchema(
                selected_candidate=selected_candidate,
                justification=data["justification"]
            )
        
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            raise ValueError(f"Failed to parse LLM output as valid JSON schema: {str(e)}")
    
    def _format_final_answer(self, parsed_response: LlmResponseSchema) -> str:
        if parsed_response.selected_candidate is None:
            return f"No candidate selected.\n\n{parsed_response.justification}"
        
        return (
            f"Selected Candidate: {parsed_response.selected_candidate.fullname} "
            f"(ID: {parsed_response.selected_candidate.candidate_id}, Rank: {parsed_response.selected_candidate.rank})\n\n"
            f"Justification: {parsed_response.justification}"
        )
    
    def _build_response_metadata(self, parsed_response: LlmResponseSchema) -> dict:
        metadata = {
            "justification": parsed_response.justification
        }
        
        if parsed_response.selected_candidate is not None:
            metadata["selected_candidate"] = {
                "fullname": parsed_response.selected_candidate.fullname,
                "candidate_id": parsed_response.selected_candidate.candidate_id,
                "rank": parsed_response.selected_candidate.rank
            }
        else:
            metadata["selected_candidate"] = None
        
        return metadata
