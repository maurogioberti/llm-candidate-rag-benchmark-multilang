from pydantic import BaseModel


class ChatSource(BaseModel):
    candidate_id: str
    section: str
    content: str
    score: float