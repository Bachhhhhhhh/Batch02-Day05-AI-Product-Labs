from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str
    api_key: Optional[str] = None
    provider: Optional[str] = "mock"  # "mock", "gemini", "openai"
    chat_history: Optional[List[dict]] = None

class AgentRequest(BaseModel):
    message: str
    provider: Optional[str] = "mock"  # "mock", "gemini", "openai"
