from pydantic import BaseModel
from typing import Dict, Any


class IndexInfo(BaseModel):
    candidates: int
    chunks: int
    points: int = 0
    provider: str
    metadata: Dict[str, Any] = {}