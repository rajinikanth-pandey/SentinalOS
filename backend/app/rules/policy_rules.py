# rules/policy_rules.py
from typing import Dict, List, Any, Union
from schemas.security_event import SecurityEvent


class PolicyEngine:

    def __init__(self):
        self.production_actions = {
            "delete_database",
            "delete_repository",
            "delete_bucket",
            "drop_database",
            "terminate_instance",
            "delete_cluster"
        }

        self.sensitive_resources = {
            "production_database",
            "repositories",
            "customer_data",
            "credentials",
            "secrets",
            "tokens",
            "iam_users"
        }

        self.cloud_tools = {
            "AWS",
            "GitHub",
            "Kubernetes",
            "Docker",
            "Azure",
            "GCP"
        }

    def evaluate(self, event: Union[Dict[str, Any], SecurityEvent]) -> Dict[str, Any]:
        """
        Evaluate policy violations for a security event.
        
        Args:
            event: Security event as dictionary or SecurityEvent object
            
        Returns:
            Dictionary with policy decision, score, and violations
        """
        violations = []
        decision = "ALLOW"

        # Convert to dict if it's a SecurityEvent object
        if isinstance(event, SecurityEvent):
            event_dict = event.model_dump()
        else:
            event_dict = event

        # -----------------------------
        # Production destructive actions
        # -----------------------------
        if (
            event_dict.get("environment") == "production"
            and event_dict.get("action") in self.production_actions
        ):
            decision = "BLOCK"
            violations.append(
                "Production destructive actions are prohibited."
            )

        # -----------------------------
        # Sensitive Resources
        # -----------------------------
        if event_dict.get("resource") in self.sensitive_resources:
            violations.append(
                "Sensitive resource detected."
            )

        # -----------------------------
        # Cloud Platform Protection
        # -----------------------------
        if event_dict.get("tool") in self.cloud_tools:
            violations.append(
                f"Critical cloud platform: {event_dict.get('tool')}"
            )

        # -----------------------------
        # Approval Requirement
        # -----------------------------
        if event_dict.get("requires_approval", False):
            violations.append(
                "Human approval required."
            )

        # -----------------------------
        # Final Decision
        # -----------------------------
        if len(violations) >= 3:
            decision = "BLOCK"
        elif len(violations) >= 1 and decision != "BLOCK":
            decision = "REVIEW"

        return {
            "policy_decision": decision,
            "policy_score": min(len(violations) * 25, 100),
            "violations": violations
        }