# rules/risk_engine.py
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime


class RiskEngine:
    """
    Deterministic rule-based risk engine for security event evaluation.
    Evaluates events based on configurable rules and weights.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Risk Engine with optional custom config path.
        
        Args:
            config_path: Path to rules.json file (optional)
        """
        self.config = self._load_config(config_path)
        self.weights = self.config.get("weights", {})
        self.thresholds = self.config.get("thresholds", {"block": 80, "review": 50})
        self.rules = self.config.get("rules", [])
        
        # Cache for performance
        self._rule_cache = {}
        
        print(f"⚖️ Risk Engine initialized with {len(self.rules)} rules")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from JSON file."""
        if config_path is None:
            # Use default path
            config_path = Path(__file__).parent / "rules.json"
        else:
            config_path = Path(config_path)
        
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"✅ Loaded rules config from: {config_path}")
                return config
            else:
                print(f"⚠️ Config file not found: {config_path}, using defaults")
                return self._get_default_config()
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration if file not found."""
        return {
            "weights": {
                "environment": {
                    "production": 30,
                    "staging": 15,
                    "development": 5,
                    "test": 5
                },
                "sensitivity": {
                    "critical": 30,
                    "high": 20,
                    "medium": 10,
                    "low": 5
                },
                "actions": {
                    "delete": 25,
                    "drop": 25,
                    "destroy": 25,
                    "remove": 20,
                    "terminate": 20,
                    "update": 10,
                    "modify": 10,
                    "create": 5,
                    "read": 0
                },
                "tools": {
                    "aws": 15,
                    "github": 15,
                    "kubernetes": 15,
                    "docker": 10,
                    "database": 15,
                    "azure": 15,
                    "gcp": 15
                },
                "resources": {
                    "secret": 25,
                    "credential": 25,
                    "password": 25,
                    "token": 25,
                    "key": 20,
                    "certificate": 20,
                    "database": 15,
                    "bucket": 15,
                    "repository": 15,
                    "pod": 10,
                    "service": 10
                },
                "context": {
                    "bulk_operation": 15,
                    "mass_delete": 20,
                    "unauthorized": 30
                }
            },
            "thresholds": {
                "block": 80,
                "review": 50
            },
            "rules": []
        }
    
    def calculate(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate risk score based on event data.
        
        Args:
            event: Security event dictionary
            
        Returns:
            Dict with risk score, decision, and reasons
        """
        score = 0
        reasons = []
        matched_rules = []
        
        # Apply rules-based evaluation
        for rule in self.rules:
            if self._evaluate_rule(rule, event):
                weight = rule.get("weight", 0)
                score += weight
                reasons.append(rule.get("reason", f"Rule {rule.get('id', 'unknown')} matched"))
                matched_rules.append({
                    "id": rule.get("id"),
                    "name": rule.get("name"),
                    "weight": weight,
                    "reason": rule.get("reason")
                })
        
        # Apply weight-based evaluation (fallback for non-rule matches)
        if not matched_rules:
            score = self._calculate_weighted_score(event)
            reasons = self._generate_weighted_reasons(event)
        
        # Cap score at 100
        score = min(score, 100)
        
        # Determine decision
        decision = self._decide(score)
        
        return {
            "rule_risk_score": score,
            "rule_decision": decision,
            "rule_reasons": reasons,
            "matched_rules": matched_rules,
            "calculation_timestamp": datetime.now().isoformat()
        }
    
    def _calculate_weighted_score(self, event: Dict[str, Any]) -> int:
        """Calculate risk score using weight-based approach."""
        score = 0
        
        # Environment weight
        env = event.get("environment", "development").lower()
        score += self.weights.get("environment", {}).get(env, 0)
        
        # Sensitivity weight
        sensitivity = event.get("sensitivity", "low").lower()
        score += self.weights.get("sensitivity", {}).get(sensitivity, 0)
        
        # Action weight
        action = event.get("action", "").lower()
        for action_key, weight in self.weights.get("actions", {}).items():
            if action_key in action:
                score += weight
                break
        
        # Tool weight
        tool = event.get("tool", "").lower()
        for tool_key, weight in self.weights.get("tools", {}).items():
            if tool_key in tool:
                score += weight
                break
        
        # Resource weight
        resource = event.get("resource", "").lower()
        for resource_key, weight in self.weights.get("resources", {}).items():
            if resource_key in resource:
                score += weight
                break
        
        # Context weights
        context = event.get("context", {})
        for context_key, weight in self.weights.get("context", {}).items():
            if context.get(context_key):
                score += weight
        
        return min(score, 100)
    
    def _generate_weighted_reasons(self, event: Dict[str, Any]) -> List[str]:
        """Generate reasons based on weighted evaluation."""
        reasons = []
        
        env = event.get("environment", "development").lower()
        if env == "production":
            reasons.append("Production environment detected.")
        
        sensitivity = event.get("sensitivity", "low").lower()
        if sensitivity == "critical":
            reasons.append("Critical resource.")
        elif sensitivity == "high":
            reasons.append("High sensitivity resource.")
        
        action = event.get("action", "").lower()
        dangerous_actions = ["delete", "drop", "destroy", "remove", "terminate"]
        if any(word in action for word in dangerous_actions):
            reasons.append("Destructive action detected.")
        
        tool = event.get("tool", "").lower()
        critical_tools = ["aws", "github", "kubernetes", "docker", "azure", "gcp"]
        if any(tool_key in tool for tool_key in critical_tools):
            reasons.append(f"Critical platform: {tool}")
        
        resource = event.get("resource", "").lower()
        sensitive_resources = ["secret", "credential", "password", "token", "key"]
        if any(word in resource for word in sensitive_resources):
            reasons.append("Sensitive credentials detected.")
        
        return reasons if reasons else ["No specific risk factors identified."]
    
    def _evaluate_rule(self, rule: Dict, event: Dict[str, Any]) -> bool:
        """
        Evaluate a rule condition against the event.
        Supports simple conditions with 'in' and 'contains' operators.
        """
        condition = rule.get("condition", "")
        
        if not condition:
            return False
        
        try:
            # Parse simple conditions like: "environment == 'production'"
            # or "action in ['delete', 'drop']"
            # or "resource contains ['secret', 'credential']"
            
            parts = condition.split()
            
            if len(parts) == 3 and parts[1] == '==':
                # Equality check: field == 'value'
                field = parts[0]
                value = parts[2].strip("'\"")
                return self._get_nested_value(event, field) == value
            
            elif ' in ' in condition:
                # Contains in list: field in ['value1', 'value2']
                field, values_str = condition.split(' in ')
                values = eval(values_str)  # Convert string list to actual list
                field_value = self._get_nested_value(event, field)
                return field_value in values
            
            elif ' contains ' in condition:
                # Contains substring: field contains ['value1', 'value2']
                field, values_str = condition.split(' contains ')
                values = eval(values_str)
                field_value = str(self._get_nested_value(event, field, ""))
                return any(value in field_value for value in values)
            
            return False
            
        except Exception as e:
            print(f"⚠️ Rule evaluation error for {rule.get('id')}: {e}")
            return False
    
    def _get_nested_value(self, obj: Dict, key: str, default: Any = None) -> Any:
        """Get nested value using dot notation (e.g., 'context.bulk_operation')."""
        keys = key.split('.')
        current = obj
        
        for k in keys:
            if isinstance(current, dict):
                current = current.get(k)
            else:
                return default
        
        return current if current is not None else default
    
    def _decide(self, score: int) -> str:
        """Determine decision based on score thresholds."""
        if score >= self.thresholds.get("block", 80):
            return "BLOCK"
        elif score >= self.thresholds.get("review", 50):
            return "REVIEW"
        return "ALLOW"
    
    def reload_config(self, config_path: Optional[str] = None):
        """Reload configuration from file."""
        self.config = self._load_config(config_path)
        self.weights = self.config.get("weights", {})
        self.thresholds = self.config.get("thresholds", {"block": 80, "review": 50})
        self.rules = self.config.get("rules", [])
        print(f"🔄 Configuration reloaded. {len(self.rules)} rules active.")
    
    def get_risk_factors(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed risk factor analysis for an event."""
        result = self.calculate(event)
        
        # Add detailed breakdown
        breakdown = {
            "environment_risk": self._get_environment_risk(event),
            "sensitivity_risk": self._get_sensitivity_risk(event),
            "action_risk": self._get_action_risk(event),
            "tool_risk": self._get_tool_risk(event),
            "resource_risk": self._get_resource_risk(event),
            "context_risk": self._get_context_risk(event)
        }
        
        result["risk_breakdown"] = breakdown
        return result
    
    def _get_environment_risk(self, event: Dict) -> int:
        env = event.get("environment", "development").lower()
        return self.weights.get("environment", {}).get(env, 0)
    
    def _get_sensitivity_risk(self, event: Dict) -> int:
        sensitivity = event.get("sensitivity", "low").lower()
        return self.weights.get("sensitivity", {}).get(sensitivity, 0)
    
    def _get_action_risk(self, event: Dict) -> int:
        action = event.get("action", "").lower()
        for key, weight in self.weights.get("actions", {}).items():
            if key in action:
                return weight
        return 0
    
    def _get_tool_risk(self, event: Dict) -> int:
        tool = event.get("tool", "").lower()
        for key, weight in self.weights.get("tools", {}).items():
            if key in tool:
                return weight
        return 0
    
    def _get_resource_risk(self, event: Dict) -> int:
        resource = event.get("resource", "").lower()
        for key, weight in self.weights.get("resources", {}).items():
            if key in resource:
                return weight
        return 0
    
    def _get_context_risk(self, event: Dict) -> int:
        context = event.get("context", {})
        total = 0
        for key, weight in self.weights.get("context", {}).items():
            if context.get(key):
                total += weight
        return total