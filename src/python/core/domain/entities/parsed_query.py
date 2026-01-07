from dataclasses import dataclass
from typing import List, Optional
from ..enums.seniority_level import SeniorityLevel
from ..enums.query_intent import QueryIntent


@dataclass(frozen=True)
class ParsedQuery:
    query_text: str
    query_intent: QueryIntent
    required_technologies: List[str]
    min_seniority_level: Optional[SeniorityLevel]
    min_years_experience: Optional[int]
