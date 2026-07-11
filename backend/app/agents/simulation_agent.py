import json
from agents.base_agent import BaseAgent


class SimulationAgent(BaseAgent):

    @property
    def system_prompt(self):

        return """
You are SentinelOS Simulation Agent.

Predict what will happen if the action executes.

Return ONLY valid JSON.

{
    "agent_name":"SimulationAgent",
    "decision":"ALLOW or BLOCK",
    "confidence":0.95,
    "risk_score":95,
    "reasoning":"Reason",
    "recommendations":[
        "Recommendation"
    ],
    "metadata":{
        "estimated_downtime":"",
        "business_impact":"",
        "affected_systems":[]
    }
}
"""

    def process_response(self, response):
        return json.loads(response)