from pydantic import BaseModel
from typing import Optional

from .chat_filters import ChatFilters


class ChatRequestDto(BaseModel):
    question: str
    filters: Optional[ChatFilters] = None