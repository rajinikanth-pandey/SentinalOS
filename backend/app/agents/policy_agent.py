import json
from agents.base_agent import BaseAgent


class PolicyAgent(BaseAgent):

    @property
    def system_prompt(self):

        return """
You are SentinelOS Policy Agent.

Evaluate whether the request violates organizational security policies.

Return ONLY valid JSON.

{
    "agent_name":"PolicyAgent",
    "decision":"ALLOW or BLOCK",
    "confidence":0.95,
    "risk_score":90,
    "reasoning":"Reason",
    "recommendations":[
        "Recommendation"
    ],
    "metadata":{
        "policy_reference":"",
        "violation":true
    }
}
"""

    def process_response(self, response):
        return json.loads(response)