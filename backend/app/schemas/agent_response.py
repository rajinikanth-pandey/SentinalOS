from pydantic import BaseModel
from typing import Optional, List
from schemas.decision import Decision

class AgentResponse(BaseModel):
    agent_name: str

    decision: Decision

    confidence: float

    risk_score: int

    reasoning: str

    recommendations: List[str] = []

    metadata: Optional[dict] = None