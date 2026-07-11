# parser/event_parser.py
import json
import re
from typing import Dict, Any, Optional
from llm.client import groq_client
from schemas.security_event import SecurityEvent


class EventParser:
    """Parses natural language prompts into structured SecurityEvent objects"""

    SYSTEM_PROMPT = """
You are SentinelOS Security Event Parser.

Convert user requests into a structured security event.

Always return ONLY valid JSON.

Schema:
{
    "actor": "User",
    "actor_type": "USER",
    "action": "",
    "resource": "",
    "tool": "",
    "environment": "development",
    "sensitivity": "low",
    "context": {}
}

Rules:
- actor: Usually "User" for CLI/API requests
- actor_type: USER, SYSTEM, SERVICE, WEBHOOK, API
- action: Use snake_case (e.g., delete_database, restart_pod, read_logs)
- resource: The target of the action
- tool: The platform/tool involved (AWS, GitHub, Kubernetes, Database, etc.)
- environment: development, staging, production, test
- sensitivity: low, medium, high, critical

Examples:

Input: "Delete production database"
Output: {
    "actor": "User",
    "actor_type": "USER",
    "action": "delete_database",
    "resource": "production_database",
    "tool": "Database",
    "environment": "production",
    "sensitivity": "critical",
    "context": {}
}

Input: "Delete AWS S3 bucket"
Output: {
    "actor": "User",
    "actor_type": "USER",
    "action": "delete_bucket",
    "resource": "S3 Bucket",
    "tool": "AWS",
    "environment": "production",
    "sensitivity": "critical",
    "context": {}
}

Input: "Read security logs"
Output: {
    "actor": "User",
    "actor_type": "USER",
    "action": "read_logs",
    "resource": "security_logs",
    "tool": "Logging System",
    "environment": "development",
    "sensitivity": "low",
    "context": {}
}

Input: "Restart Kubernetes pod"
Output: {
    "actor": "User",
    "actor_type": "USER",
    "action": "restart_pod",
    "resource": "pod",
    "tool": "Kubernetes",
    "environment": "production",
    "sensitivity": "medium",
    "context": {}
}

Input: "Delete all GitHub repositories"
Output: {
    "actor": "User",
    "actor_type": "USER",
    "action": "delete_repository",
    "resource": "repositories",
    "tool": "GitHub",
    "environment": "production",
    "sensitivity": "critical",
    "context": {}
}

Return ONLY valid JSON. No markdown, no extra text.
"""

    def __init__(self, use_mock: bool = False):
        """Initialize EventParser with optional mock mode for testing"""
        self.use_mock = use_mock

    def parse(self, prompt: str) -> SecurityEvent:
        """
        Parse a natural language prompt into a SecurityEvent.
        
        Args:
            prompt: Natural language request
            
        Returns:
            SecurityEvent object
        """
        try:
            # Get response from LLM
            response = self._get_llm_response(prompt)
            
            # Clean the response
            cleaned_response = self._clean_response(response)
            
            # Parse JSON
            data = json.loads(cleaned_response)
            
            # Validate and create SecurityEvent
            event = self._create_security_event(data)
            
            # Enrich with additional context
            event = self._enrich_event(event, prompt)
            
            return event
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error in EventParser: {e}")
            print(f"Response: {response}")
            # Return a default event
            return self._create_fallback_event(prompt)
            
        except Exception as e:
            print(f"❌ Error in EventParser: {e}")
            return self._create_fallback_event(prompt)

    def _get_llm_response(self, prompt: str) -> str:
        """Get response from LLM or mock"""
        if self.use_mock:
            return self._get_mock_response(prompt)
        return groq_client.chat(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=prompt
        )

    def _clean_response(self, response: str) -> str:
        """Clean the response to extract valid JSON"""
        if not response or not response.strip():
            return "{}"
        
        # Remove markdown code blocks
        response = re.sub(r'^```json\s*', '', response)
        response = re.sub(r'^```\s*', '', response)
        response = re.sub(r'```$', '', response)
        response = response.strip()
        
        # Try to find JSON if response contains other text
        if not response.startswith('{'):
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                response = json_match.group()
        
        return response

    def _create_security_event(self, data: Dict[str, Any]) -> SecurityEvent:
        """Create a SecurityEvent from parsed data"""
        # Set defaults
        defaults = {
            "actor": "User",
            "actor_type": "USER",
            "action": "unknown",
            "resource": "unknown",
            "tool": "Unknown",
            "environment": "development",
            "sensitivity": "low",
            "context": {}
        }
        
        # Merge with provided data
        event_data = {**defaults, **data}
        
        # Ensure required fields
        if not event_data.get("action") or event_data["action"] == "unknown":
            event_data["action"] = "process_request"
        
        # Create SecurityEvent
        return SecurityEvent(**event_data)

    def _enrich_event(self, event: SecurityEvent, prompt: str) -> SecurityEvent:
        """Enrich the event with additional derived information"""
        # Add original prompt to context
        event.context["original_prompt"] = prompt
        
        # Add timestamp
        from datetime import datetime
        event.context["parsed_at"] = datetime.now().isoformat()
        
        # Calculate risk level
        event.context["risk_level"] = event.get_risk_level()
        
        # Determine if approval is required
        event.requires_approval = (
            event.is_critical() or 
            event.sensitivity.lower() in ["high", "critical"] or
            "delete" in event.action.lower() or
            "remove" in event.action.lower()
        )
        
        return event

    def _create_fallback_event(self, prompt: str) -> SecurityEvent:
        """Create a fallback event when parsing fails"""
        # Try to detect action from prompt
        action = "process_request"
        if "delete" in prompt.lower() or "remove" in prompt.lower():
            action = "delete_resource"
        elif "restart" in prompt.lower():
            action = "restart_service"
        elif "read" in prompt.lower() or "view" in prompt.lower():
            action = "read_resource"
        elif "create" in prompt.lower() or "add" in prompt.lower():
            action = "create_resource"
        
        # Detect environment
        environment = "development"
        if "prod" in prompt.lower() or "production" in prompt.lower():
            environment = "production"
        elif "stage" in prompt.lower():
            environment = "staging"
        
        # Detect sensitivity
        sensitivity = "medium"
        if "critical" in prompt.lower() or "secret" in prompt.lower():
            sensitivity = "critical"
        elif "high" in prompt.lower():
            sensitivity = "high"
        elif "low" in prompt.lower():
            sensitivity = "low"
        
        return SecurityEvent(
            actor="User",
            actor_type="USER",
            action=action,
            resource="unknown",
            tool="Unknown",
            environment=environment,
            sensitivity=sensitivity,
            context={
                "original_prompt": prompt,
                "parsed_at": __import__('datetime').datetime.now().isoformat(),
                "is_fallback": True,
                "error": "Parsing failed, using fallback"
            }
        )

    def _get_mock_response(self, prompt: str) -> str:
        """Generate mock responses for testing"""
        prompt_lower = prompt.lower()
        
        if "delete" in prompt_lower and "database" in prompt_lower:
            return json.dumps({
                "actor": "User",
                "actor_type": "USER",
                "action": "delete_database",
                "resource": "production_database",
                "tool": "Database",
                "environment": "production",
                "sensitivity": "critical",
                "context": {}
            })
        elif "delete" in prompt_lower and ("s3" in prompt_lower or "bucket" in prompt_lower):
            return json.dumps({
                "actor": "User",
                "actor_type": "USER",
                "action": "delete_bucket",
                "resource": "S3 Bucket",
                "tool": "AWS",
                "environment": "production",
                "sensitivity": "critical",
                "context": {}
            })
        elif "restart" in prompt_lower and "kubernetes" in prompt_lower:
            return json.dumps({
                "actor": "User",
                "actor_type": "USER",
                "action": "restart_pod",
                "resource": "pod",
                "tool": "Kubernetes",
                "environment": "production",
                "sensitivity": "medium",
                "context": {}
            })
        elif "read" in prompt_lower and "log" in prompt_lower:
            return json.dumps({
                "actor": "User",
                "actor_type": "USER",
                "action": "read_logs",
                "resource": "security_logs",
                "tool": "Logging System",
                "environment": "development",
                "sensitivity": "low",
                "context": {}
            })
        elif "delete" in prompt_lower and "github" in prompt_lower:
            return json.dumps({
                "actor": "User",
                "actor_type": "USER",
                "action": "delete_repository",
                "resource": "repositories",
                "tool": "GitHub",
                "environment": "production",
                "sensitivity": "critical",
                "context": {}
            })
        else:
            return json.dumps({
                "actor": "User",
                "actor_type": "USER",
                "action": "process_request",
                "resource": "unknown",
                "tool": "Unknown",
                "environment": "development",
                "sensitivity": "medium",
                "context": {}
            })