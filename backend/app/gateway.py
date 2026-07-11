# api/gateway.py
import re
from typing import Dict, Any, Tuple
from datetime import datetime

from orchestrator.orchestrator import SentinelOrchestrator
from chat import chat_service
from database.models import AuditModel


class SentinelGateway:
    """
    Unified gateway that processes every prompt through security analysis
    before allowing it to reach the LLM.
    """
    
    def __init__(self):
        self.orchestrator = SentinelOrchestrator()
        
        # Patterns for harmless questions (bypass security analysis)
        self.harmless_patterns = [
            r'^(what|how|why|when|where|who|which|can|could|would|will|is|are|does|do|did|has|have|should|could|may|might)\s',
            r'\?$',  # Questions ending with ?
            r'^explain\s',
            r'^tell me about\s',
            r'^describe\s',
            r'^define\s',
            r'^what is\s',
            r'^how to\s',
            r'^how does\s',
            r'^what does\s',
            r'^what are\s',
            r'^whats\s',
        ]
        
        # Keywords that might indicate harmless questions
        self.harmless_keywords = [
            'learn', 'learning', 'understand', 'understanding',
            'explain', 'explanation', 'describe', 'definition',
            'meaning', 'purpose', 'function', 'why', 'how',
            'example', 'examples', 'tutorial', 'guide',
            'beginner', 'introduction', 'overview', 'basics',
            'what', 'when', 'where', 'who', 'which'
        ]
    
    def _is_harmless_question(self, prompt: str) -> bool:
        """Check if the prompt is a harmless question that doesn't need security analysis."""
        prompt_lower = prompt.lower().strip()
        
        # Check for question patterns
        for pattern in self.harmless_patterns:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                return True
        
        # Check for harmless keywords
        for keyword in self.harmless_keywords:
            if keyword in prompt_lower:
                return True
        
        # Check if it's a short question
        if len(prompt_lower) < 50 and ('?' in prompt_lower):
            return True
        
        return False
    
    def _is_clearly_dangerous(self, prompt: str) -> bool:
        """Quick check for clearly dangerous requests."""
        prompt_lower = prompt.lower().strip()
        
        dangerous_patterns = [
            r'delete.*database',
            r'drop.*table',
            r'delete.*production',
            r'delete.*aws.*bucket',
            r'delete.*github.*repo',
            r'delete.*repository',
            r'delete.*all.*data',
            r'remove.*all.*data',
            r'truncate.*table',
            r'rm\s+-rf',
            r'delete.*credential',
            r'delete.*secret',
            r'delete.*password',
            r'destroy.*production',
            r'terminate.*instance',
            r'delete.*s3.*bucket',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, prompt_lower):
                return True
        
        return False
    
    def process(self, prompt: str, user_id: str = None, session_id: str = None) -> Dict[str, Any]:
        """
        Process a user prompt through the security pipeline.
        
        Returns:
            Dict with mode ('chat' or 'blocked') and appropriate response
        """
        # STEP 1: Check if it's a clearly dangerous request (quick pre-filter)
        if self._is_clearly_dangerous(prompt):
            # Still run full analysis for detailed reporting
            analysis = self.orchestrator.analyze(prompt)
            return self._create_blocked_response(prompt, analysis, user_id, session_id)
        
        # STEP 2: Check if it's a harmless question (bypass security)
        if self._is_harmless_question(prompt):
            print(f"✅ Detected harmless question, bypassing security analysis: {prompt[:50]}...")
            return self._process_as_chat(prompt, user_id, session_id)
        
        # STEP 3: For everything else, run full security analysis
        analysis = self.orchestrator.analyze(prompt)
        
        # STEP 4: Check if blocked
        if analysis.get("final_decision") == "BLOCK":
            return self._create_blocked_response(prompt, analysis, user_id, session_id)
        
        # STEP 5: Allow and forward to chat
        return self._process_as_chat(prompt, user_id, session_id, analysis)
    
    def _process_as_chat(self, prompt: str, user_id: str = None, 
                         session_id: str = None, analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process as a chat request."""
        try:
            chat_response = chat_service.chat(prompt)
            
            # Create analysis if not provided
            if analysis is None:
                analysis = {
                    "final_decision": "ALLOW",
                    "overall_risk": 0,
                    "confidence": 0.95,
                    "summary": "Harmless question - no security analysis needed",
                    "recommendations": []
                }
            
            response = {
                "timestamp": datetime.now().isoformat(),
                "mode": "chat",
                "analysis": {
                    "final_decision": analysis.get("final_decision", "ALLOW"),
                    "overall_risk": analysis.get("overall_risk", 0),
                    "confidence": analysis.get("confidence", 0.95),
                    "summary": analysis.get("summary", "Request processed as chat"),
                    "recommendations": analysis.get("recommendations", [])
                },
                "chat": chat_response
            }
            
            # Log the interaction
            self._log_interaction(prompt, "chat", analysis, user_id, session_id, chat_response)
            
            return response
            
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "mode": "chat",
                "analysis": {
                    "final_decision": "ERROR",
                    "overall_risk": 0,
                    "confidence": 0,
                    "summary": f"Error processing chat: {str(e)}",
                    "recommendations": []
                },
                "chat": {
                    "response": f"I apologize, but I encountered an error: {str(e)}",
                    "error": str(e)
                }
            }
    
    def _create_blocked_response(self, prompt: str, analysis: Dict[str, Any], 
                                  user_id: str = None, session_id: str = None) -> Dict[str, Any]:
        """Create a blocked response."""
        response = {
            "timestamp": datetime.now().isoformat(),
            "mode": "blocked",
            "analysis": {
                "final_decision": analysis.get("final_decision", "BLOCK"),
                "overall_risk": analysis.get("overall_risk", 0),
                "confidence": analysis.get("confidence", 0),
                "summary": analysis.get("summary", "Request blocked by security policy"),
                "recommendations": analysis.get("recommendations", [])
            },
            "security_report": {
                "event": analysis.get("event", {}),
                "rule_result": analysis.get("rule_result", {}),
                "policy_result": analysis.get("policy_result", {}),
                "agent_results": analysis.get("agent_results", [])
            },
            "block_reason": self._generate_block_reason(analysis),
            "suggestions": self._generate_suggestions(analysis)
        }
        
        # Log the blocked request
        self._log_interaction(prompt, "blocked", analysis, user_id, session_id)
        
        return response
    
    def _generate_block_reason(self, analysis: Dict[str, Any]) -> str:
        """Generate a user-friendly block reason"""
        reasons = []
        
        # Check rule engine reasons
        rule_result = analysis.get("rule_result", {})
        if rule_result.get("rule_reasons"):
            reasons.extend(rule_result["rule_reasons"][:3])
        
        # Check policy violations
        policy_result = analysis.get("policy_result", {})
        if policy_result.get("violations"):
            reasons.extend(policy_result["violations"][:2])
        
        # Add risk score context
        risk = analysis.get("overall_risk", 0)
        if risk >= 90:
            reasons.append("Extremely high risk detected")
        elif risk >= 80:
            reasons.append("High risk detected")
        
        if not reasons:
            reasons.append("Request blocked by security policy")
        
        return " | ".join(reasons[:3])
    
    def _generate_suggestions(self, analysis: Dict[str, Any]) -> list:
        """Generate suggestions for the user"""
        suggestions = []
        
        # Add recommendations from consensus
        recommendations = analysis.get("recommendations", [])
        if recommendations:
            suggestions.extend(recommendations[:2])
        
        # Add specific suggestions based on action
        event = analysis.get("event", {})
        action = event.get("action", "")
        
        if "delete" in action.lower():
            suggestions.append("Consider using a backup or snapshot before any destructive operation")
            suggestions.append("Verify you have the correct environment selected")
        
        if event.get("environment") == "production":
            suggestions.append("Consider testing in a non-production environment first")
        
        if not suggestions:
            suggestions.append("Contact your security team for assistance")
        
        return suggestions[:3]
    
    def _log_interaction(self, prompt: str, mode: str, analysis: Dict[str, Any], 
                        user_id: str = None, session_id: str = None, 
                        chat_response: Dict[str, Any] = None):
        """Log the interaction to the database"""
        try:
            record = {
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "action": analysis.get("event", {}).get("action", "unknown") if analysis else "unknown",
                "tool": analysis.get("event", {}).get("tool", "unknown") if analysis else "unknown",
                "environment": analysis.get("event", {}).get("environment", "development") if analysis else "development",
                "sensitivity": analysis.get("event", {}).get("sensitivity", "low") if analysis else "low",
                "decision": analysis.get("final_decision", "ALLOW") if analysis else "ALLOW",
                "risk_score": analysis.get("overall_risk", 0) if analysis else 0,
                "confidence": analysis.get("confidence", 0.5) if analysis else 0.5,
                "summary": analysis.get("summary", "") if analysis else "",
                "mode": mode,
                "user_id": user_id or "anonymous",
                "session_id": session_id or "unknown",
                "chat_response": chat_response.get("response") if chat_response else None,
                "raw_analysis": analysis
            }
            
            AuditModel.insert(record)
        except Exception as e:
            print(f"⚠️ Failed to log interaction: {e}")


# Singleton instance
gateway = SentinelGateway()