import json
import re
from typing import List, Dict, Any
from agents.base_agent import BaseAgent

class PlannerAgent(BaseAgent):

    @property
    def system_prompt(self):
        return """
You are SentinelOS Planner Agent.

Determine which security agents should analyze the request.

Available agents:
- ThreatAgent
- PolicyAgent
- SimulationAgent
- ExecutiveAgent

Rules:
- If request involves delete, remove, drop, production, database, secrets,
  credentials, github, aws, cloud -> return ALL agents.

Return ONLY valid JSON.

Example:

{
    "agents":[
        "ThreatAgent",
        "PolicyAgent",
        "SimulationAgent",
        "ExecutiveAgent"
    ]
}
"""

    def process_response(self, response: str) -> Dict[str, Any]:
        """Process and validate the planner response"""
        try:
            # Try to parse as JSON
            parsed = json.loads(response)
            
            # Ensure 'agents' key exists
            if "agents" not in parsed:
                parsed["agents"] = self._extract_agents_from_text(response)
            
            # Ensure agents is a list
            if not isinstance(parsed["agents"], list):
                parsed["agents"] = []
            
            # Filter to only valid agent names
            valid_agents = ["ThreatAgent", "PolicyAgent", "SimulationAgent", "ExecutiveAgent"]
            parsed["agents"] = [agent for agent in parsed["agents"] if agent in valid_agents]
            
            # If no valid agents, use all
            if not parsed["agents"]:
                parsed["agents"] = valid_agents
                
            return parsed
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error in PlannerAgent: {e}")
            print(f"Raw response: {response[:200]}...")
            
            # Try to extract agents from text
            agents = self._extract_agents_from_text(response)
            
            return {
                "agents": agents,
                "reasoning": "Extracted from text response"
            }
            
        except Exception as e:
            print(f"Error in PlannerAgent.process_response: {e}")
            # Return all agents as fallback
            return {
                "agents": ["ThreatAgent", "PolicyAgent", "SimulationAgent", "ExecutiveAgent"],
                "reasoning": f"Error: {str(e)}"
            }

    def _extract_agents_from_text(self, text: str) -> List[str]:
        """Extract agent names from plain text response"""
        valid_agents = ["ThreatAgent", "PolicyAgent", "SimulationAgent", "ExecutiveAgent"]
        found_agents = []
        
        # Search for agent names in the text
        for agent in valid_agents:
            if agent.lower() in text.lower():
                found_agents.append(agent)
        
        # If no agents found, return all
        if not found_agents:
            # Check for keywords that might indicate all agents needed
            keywords = ["delete", "remove", "drop", "production", "database", 
                       "secrets", "credentials", "github", "aws", "cloud"]
            text_lower = text.lower()
            
            for keyword in keywords:
                if keyword in text_lower:
                    return valid_agents
            
            # Default: return all agents
            return valid_agents
            
        return found_agents