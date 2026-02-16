from pydantic import BaseModel


class LlmJustificationSchema(BaseModel):
    """LLM output schema for justification only."""
    justification: str
