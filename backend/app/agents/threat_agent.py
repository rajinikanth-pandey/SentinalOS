import json
from agents.base_agent import BaseAgent


class ThreatAgent(BaseAgent):

    @property
    def system_prompt(self):

        return """
You are SentinelOS Threat Agent.

Analyze whether the request is malicious.

Return ONLY valid JSON.

{
    "agent_name":"ThreatAgent",
    "decision":"ALLOW or BLOCK",
    "confidence":0.95,
    "risk_score":95,
    "reasoning":"Reason",
    "recommendations":[
        "Recommendation"
    ],
    "metadata":{
        "attack_type":"",
        "severity":""
    }
}
"""

    def process_response(self, response):
        return json.loads(response)