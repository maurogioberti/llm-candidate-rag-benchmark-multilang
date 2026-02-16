"""Custom exception for structured LLM output validation failures."""

DEFAULT_MESSAGE = "Failed to extract valid structured output from LLM response"


class LlmOutputValidationError(Exception):
    """Raised when LLM output cannot be parsed into the expected structured format."""
    
    def __init__(self, message: str = DEFAULT_MESSAGE, raw_output: str | None = None):
        super().__init__(message)
        self.raw_output = raw_output
