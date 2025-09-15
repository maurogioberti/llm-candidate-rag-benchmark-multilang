from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from .chat_source import ChatSource


class ChatResult(BaseModel):
    answer: str
    sources: List[ChatSource]
    metadata: Optional[Dict[str, Any]] = None