from pydantic import BaseModel
from typing import Dict, Any


class LlmInstructionRecord(BaseModel):
    row_id: int
    instruction: str
    input: Dict[str, Any]
    output: Dict[str, Any]
    metadata: Dict[str, Any] = {}