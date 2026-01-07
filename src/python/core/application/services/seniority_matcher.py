from typing import Optional, Dict
from ...domain.enums.seniority_level import SeniorityLevel
from ...domain.configuration.query_parsing_config import QueryParsingConfig


class SeniorityMatcher:
    def __init__(self, config: QueryParsingConfig):
        self._config = config
        self._token_map = self._build_token_map()
    
    def _build_token_map(self) -> Dict[str, SeniorityLevel]:
        mapping = {}
        for level, tokens in self._config.seniority_tokens.items():
            for token in tokens:
                mapping[token.lower()] = level
        return mapping
    
    def match(self, query_text: str) -> Optional[SeniorityLevel]:
        query_lower = query_text.lower()
        
        for token, level in self._token_map.items():
            if token in query_lower:
                return level
        
        return None
