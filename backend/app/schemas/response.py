from pydantic import BaseModel
from typing import List

from schemas.agent_response import AgentResponse
from schemas.decision import Decision


class AnalyzeResponse(BaseModel):

    final_decision: Decision

    overall_risk: int

    confidence: float

    summary: str

    agent_results: List[AgentResponse]