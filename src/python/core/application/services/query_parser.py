from ...domain.entities.parsed_query import ParsedQuery
from ...domain.enums.query_intent import QueryIntent
from ...domain.configuration.query_parsing_config import (
    QueryParsingConfig,
    DEFAULT_QUERY_PARSING_CONFIG
)
from .seniority_matcher import SeniorityMatcher
from .technology_matcher import TechnologyMatcher
from .experience_parser import ExperienceParser


class QueryParser:
    def __init__(self, config: QueryParsingConfig = None):
        self._config = config or DEFAULT_QUERY_PARSING_CONFIG
        self._seniority_matcher = SeniorityMatcher(self._config)
        self._technology_matcher = TechnologyMatcher(self._config)
        self._experience_parser = ExperienceParser()
    
    def parse(self, query_text: str) -> ParsedQuery:
        query_intent = self._extract_intent(query_text)
        required_technologies = self._technology_matcher.extract_technologies(query_text)
        min_seniority_level = self._seniority_matcher.match(query_text)
        min_years_experience = self._experience_parser.extract_years(query_text)
        
        return ParsedQuery(
            query_text=query_text,
            query_intent=query_intent,
            required_technologies=required_technologies,
            min_seniority_level=min_seniority_level,
            min_years_experience=min_years_experience
        )
    
    def _extract_intent(self, query_text: str) -> QueryIntent:
        query_lower = query_text.lower()
        
        for intent_key, keywords in self._config.intent_keywords.items():
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    return self._map_intent_key(intent_key)
        
        return QueryIntent.GENERAL
    
    def _map_intent_key(self, intent_key: str) -> QueryIntent:
        mapping = {
            "find_best": QueryIntent.FIND_BEST,
            "list_all": QueryIntent.LIST_ALL,
            "compare": QueryIntent.COMPARE,
            "explain": QueryIntent.EXPLAIN,
        }
        return mapping.get(intent_key, QueryIntent.GENERAL)
