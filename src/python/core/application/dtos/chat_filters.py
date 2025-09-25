from pydantic import BaseModel
from typing import Optional, List


class ChatFilters(BaseModel):
    prepared: Optional[bool] = None
    english_min: Optional[str] = None
    candidate_ids: Optional[List[str]] = None