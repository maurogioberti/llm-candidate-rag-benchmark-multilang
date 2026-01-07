from dataclasses import dataclass
from typing import Optional


@dataclass
class SelectedCandidate:
    fullname: str
    candidate_id: str
    rank: int


@dataclass
class LlmResponseSchema:
    selected_candidate: Optional[SelectedCandidate]
    justification: str
