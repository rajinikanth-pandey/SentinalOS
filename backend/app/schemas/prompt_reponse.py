# schemas/prompt_response.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class AnalysisSummary(BaseModel):
    """Summary of security analysis"""
    final_decision: str
    overall_risk: int
    confidence: float
    summary: str
    recommendations: List[str] = []


class PromptResponse(BaseModel):
    """
    Unified response model for the /prompt endpoint.
    
    Two modes:
    - "chat": Request was safe, returned AI response
    - "blocked": Request was dangerous, returned security report
    """
    mode: str  # "chat" or "blocked"
    timestamp: str
    
    # Always present
    analysis: AnalysisSummary
    
    # Present when mode == "chat"
    chat: Optional[Dict[str, Any]] = None
    
    # Present when mode == "blocked"
    security_report: Optional[Dict[str, Any]] = None
    block_reason: Optional[str] = None
    suggestions: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example_chat": {
                "mode": "chat",
                "timestamp": "2026-07-11T10:00:00",
                "analysis": {
                    "final_decision": "ALLOW",
                    "overall_risk": 12,
                    "confidence": 0.95,
                    "summary": "Request is safe",
                    "recommendations": []
                },
                "chat": {
                    "response": "SQL Injection is a code injection technique...",
                    "temperature": 0.7,
                    "timestamp": "2026-07-11T10:00:00"
                }
            },
            "example_blocked": {
                "mode": "blocked",
                "timestamp": "2026-07-11T10:00:00",
                "analysis": {
                    "final_decision": "BLOCK",
                    "overall_risk": 99,
                    "confidence": 0.98,
                    "summary": "High risk operation blocked",
                    "recommendations": [
                        "Obtain explicit approval from authorized personnel",
                        "Follow established change management procedures"
                    ]
                },
                "security_report": {
                    "event": {
                        "action": "delete_database",
                        "environment": "production",
                        "sensitivity": "critical"
                    },
                    "rule_result": {
                        "rule_risk_score": 85,
                        "rule_decision": "BLOCK"
                    },
                    "policy_result": {
                        "policy_decision": "BLOCK",
                        "violations": [
                            "Production destructive actions are prohibited.",
                            "Sensitive resource detected."
                        ]
                    }
                },
                "block_reason": "Production environment detected | Critical resource | Destructive action detected",
                "suggestions": [
                    "Consider using a backup or snapshot first",
                    "Verify you have the correct environment selected",
                    "Contact your security team for assistance"
                ]
            }
        }