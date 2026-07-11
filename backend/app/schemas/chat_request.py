# schemas/chat_request.py
from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    prompt: str
    temperature: Optional[float] = 0.7
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "What is Kubernetes?",
                "temperature": 0.7
            }
        }