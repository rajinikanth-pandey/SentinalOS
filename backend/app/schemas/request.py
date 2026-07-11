from pydantic import BaseModel

class AnalyzeRequest(BaseModel):
    prompt: str
    session_id: str | None = None
    user_id: str | None = None