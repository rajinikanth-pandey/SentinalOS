import json
from agents.base_agent import BaseAgent


class ExecutiveAgent(BaseAgent):

    @property
    def system_prompt(self):

        return """
You are SentinelOS Executive Agent.

Summarize all security findings.

Return ONLY valid JSON.

{
    "agent_name":"ExecutiveAgent",
    "decision":"ALLOW or BLOCK",
    "confidence":0.95,
    "risk_score":90,
    "reasoning":"Executive summary",
    "recommendations":[
        "Recommendation"
    ],
    "metadata":{
        "priority":"",
        "business_risk":""
    }
}
"""

    def process_response(self, response):
        return json.loads(response)