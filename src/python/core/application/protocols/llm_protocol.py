from typing import Protocol, List


class LlmClient(Protocol):
    
    def invoke(self, prompt: str, **kwargs) -> str:
        ...
    
    def batch(self, prompts: List[str], **kwargs) -> List[str]:
        ...