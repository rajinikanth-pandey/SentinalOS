# schemas/security_event.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum


class ActorType(str, Enum):
    USER = "USER"
    SYSTEM = "SYSTEM"
    SERVICE = "SERVICE"
    WEBHOOK = "WEBHOOK"
    API = "API"


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"
    UNKNOWN = "unknown"


class Sensitivity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEvent(BaseModel):
    """Structured security event for SentinelOS processing"""
    
    # Required fields
    actor: str = Field(..., description="Who performed the action")
    actor_type: str = Field(..., description="Type of actor (USER, SYSTEM, SERVICE, etc.)")
    action: str = Field(..., description="The action being performed")
    
    # Optional fields
    resource: Optional[str] = Field(None, description="Target resource")
    tool: Optional[str] = Field(None, description="Tool or platform being used")
    environment: str = Field(default="development", description="Environment context")
    sensitivity: str = Field(default="low", description="Sensitivity level")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    
    # Additional derived fields
    risk_score: Optional[int] = Field(None, description="Calculated risk score 0-100")
    urgency: Optional[str] = Field(None, description="Urgency level: low, medium, high, critical")
    requires_approval: bool = Field(default=False, description="Whether approval is required")
    
    class Config:
        json_schema_extra = {
            "example": {
                "actor": "JohnDoe",
                "actor_type": "USER",
                "action": "delete_database",
                "resource": "production_db",
                "tool": "AWS Console",
                "environment": "production",
                "sensitivity": "critical",
                "context": {
                    "ip": "192.168.1.100",
                    "timestamp": "2026-07-10T22:23:27.641724"
                },
                "requires_approval": True
            }
        }
    
    def is_critical(self) -> bool:
        """Check if the event is critical"""
        return self.sensitivity.lower() == "critical" or self.environment.lower() == "production"
    
    def get_risk_level(self) -> str:
        """Get risk level based on sensitivity and environment"""
        risk_matrix = {
            "development": {"low": "low", "medium": "medium", "high": "medium", "critical": "high"},
            "staging": {"low": "low", "medium": "medium", "high": "high", "critical": "high"},
            "production": {"low": "medium", "medium": "high", "high": "high", "critical": "critical"},
            "test": {"low": "low", "medium": "low", "high": "medium", "critical": "medium"},
        }
        
        env = self.environment.lower()
        sens = self.sensitivity.lower()
        
        return risk_matrix.get(env, {}).get(sens, "medium")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/processing"""
        return self.model_dump(exclude_none=True)