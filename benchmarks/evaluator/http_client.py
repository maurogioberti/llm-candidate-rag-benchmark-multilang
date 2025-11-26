import httpx


class ChatbotClient:
    CHAT_ENDPOINT = "/chat"
    QUESTION_KEY = "question"
    ANSWER_KEY = "answer"
    DEFAULT_TIMEOUT = 30.0
    
    def __init__(self, base_url: str, timeout: float = DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
    
    async def ask_question(self, client: httpx.AsyncClient, question: str) -> str:
        url = f"{self.base_url}{self.CHAT_ENDPOINT}"
        payload = {self.QUESTION_KEY: question}
        
        try:
            response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                return data.get(self.ANSWER_KEY, "")
            
            return f"Error: HTTP {response.status_code}"
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def __repr__(self) -> str:
        return f"ChatbotClient(base_url='{self.base_url}')"
