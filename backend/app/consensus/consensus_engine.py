# consensus/consensus_engine.py (updated)
from collections import Counter
from typing import List, Dict, Any


class ConsensusEngine:

    def __init__(self):
        # Weight for different agent types
        self.agent_weights = {
            "RuleEngine": 1.2,      # Rule engine is deterministic
            "PolicyAgent": 1.1,     # Policy is important
            "ThreatAgent": 1.0,
            "SimulationAgent": 1.0,
            "ExecutiveAgent": 1.3   # Executive decisions carry more weight
        }
    
    def decide(self, agent_results: List[Dict]) -> Dict[str, Any]:
        if not agent_results:
            return {
                "final_decision": "ALLOW",
                "overall_risk": 0,
                "confidence": 0.0,
                "summary": "No agents executed.",
                "agent_results": []
            }

        # Normalize agent results
        normalized_results = []
        for agent in agent_results:
            normalized = self._normalize_agent_result(agent)
            normalized_results.append(normalized)

        # Weighted majority decision
        decision_weights = {}
        for agent in normalized_results:
            decision = agent.get("decision", "REVIEW")
            agent_name = agent.get("agent_name", "Unknown")
            weight = self.agent_weights.get(agent_name, 1.0)
            
            # Increase weight if agent is deterministic
            if agent.get("is_deterministic", False):
                weight *= 1.2
            
            decision_weights[decision] = decision_weights.get(decision, 0) + weight
        
        # Get decision with highest weight
        final_decision = max(decision_weights, key=decision_weights.get)
        
        # Calculate weighted risk
        weighted_risks = []
        for agent in normalized_results:
            risk = agent.get("risk_score", 50)
            agent_name = agent.get("agent_name", "Unknown")
            weight = self.agent_weights.get(agent_name, 1.0)
            weighted_risks.append(risk * weight)
        
        total_weight = sum(self.agent_weights.get(a.get("agent_name", "Unknown"), 1.0) 
                          for a in normalized_results)
        avg_risk = round(sum(weighted_risks) / total_weight) if total_weight > 0 else 50

        # Calculate weighted confidence
        weighted_confidence = []
        for agent in normalized_results:
            confidence = agent.get("confidence", 0.5)
            agent_name = agent.get("agent_name", "Unknown")
            weight = self.agent_weights.get(agent_name, 1.0)
            weighted_confidence.append(confidence * weight)
        
        avg_confidence = round(sum(weighted_confidence) / total_weight, 2) if total_weight > 0 else 0.5

        # Merge recommendations
        recommendations = []
        for agent in normalized_results:
            recs = agent.get("recommendations", [])
            if isinstance(recs, list):
                recommendations.extend(recs)
            elif recs:
                recommendations.append(str(recs))
        
        recommendations = list(set(recommendations))

        # Build summary
        summary = (
            f"{len(agent_results)} agents (including Rule Engine) analyzed the request. "
            f"Weighted decision: {final_decision}. "
            f"Risk Score: {avg_risk}/100."
        )

        return {
            "final_decision": final_decision,
            "overall_risk": avg_risk,
            "confidence": avg_confidence,
            "summary": summary,
            "recommendations": recommendations,
            "agent_results": normalized_results,
            "decision_weights": decision_weights,
            "weighted_analysis": True
        }

    def _normalize_agent_result(self, agent: Dict) -> Dict:
        """Convert various agent output formats to a standard format."""
        if all(key in agent for key in ["decision", "risk_score", "confidence"]):
            return agent
        
        return {
            "decision": agent.get("decision", "REVIEW"),
            "risk_score": agent.get("risk_score", 50),
            "confidence": agent.get("confidence", 0.5),
            "agent_name": agent.get("agent_name", "Unknown"),
            "recommendations": agent.get("recommendations", []),
            "reason": agent.get("reason", agent.get("reasoning", "No reason provided")),
            "is_deterministic": agent.get("is_deterministic", False),
            "matched_rules": agent.get("matched_rules", [])
        }