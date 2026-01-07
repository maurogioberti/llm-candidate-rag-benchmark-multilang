from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class RankedCandidate:
    candidate_id: str
    documents: List[str]
    metadata: Dict[str, Any]
    max_score: float
    all_scores: List[float]
    technical_score: float
    seniority_score: float
    leadership_score: float
    experience_score: float
    total_score: float
