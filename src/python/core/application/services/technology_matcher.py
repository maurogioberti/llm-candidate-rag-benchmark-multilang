from typing import List
import re
from ...domain.configuration.query_parsing_config import QueryParsingConfig


class TechnologyMatcher:
    def __init__(self, config: QueryParsingConfig):
        self._config = config
    
    def extract_technologies(self, query_text: str) -> List[str]:
        technologies = []
        query_lower = query_text.lower()
        
        matched_tokens = set()
        
        for token, normalized in self._config.technology_synonyms.items():
            pattern = r'\b' + re.escape(token.lower()) + r'\b'
            if re.search(pattern, query_lower):
                matched_tokens.add(normalized)
        
        return sorted(list(matched_tokens))
