import re
from typing import Optional


class ExperienceParser:
    def __init__(self):
        self._patterns = [
            (r'(\d+)\+?\s*(?:years?|yrs?)', r'\1'),
            (r'at least (\d+)\s*(?:years?|yrs?)', r'\1'),
            (r'minimum (\d+)\s*(?:years?|yrs?)', r'\1'),
            (r'min (\d+)\s*(?:years?|yrs?)', r'\1'),
            (r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)', r'\1'),
        ]
    
    def extract_years(self, query_text: str) -> Optional[int]:
        query_lower = query_text.lower()
        
        for pattern, replacement in self._patterns:
            match = re.search(pattern, query_lower)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue
        
        return None
