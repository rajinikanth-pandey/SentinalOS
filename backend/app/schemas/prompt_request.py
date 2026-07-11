# schemas/prompt_request.py
from pydantic import BaseModel
from typing import Optional


class PromptRequest(BaseModel):
    """
    Unified request model for the single /prompt endpoint.
    This is the only endpoint users interact with.
    """
    prompt: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Delete production database",
                "user_id": "user_123",
                "session_id": "session_456"
            }
        }