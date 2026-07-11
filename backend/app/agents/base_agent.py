# agents/base_agent.py
import json
import re
from abc import ABC, abstractmethod
from llm.client import groq_client

class BaseAgent(ABC):

    def __init__(self):
        self.name = self.__class__.__name__

    @property
    @abstractmethod
    def system_prompt(self):
        pass

    @abstractmethod
    def process_response(self, response):
        pass

    def clean_response(self, response):
        """Clean the response to extract valid content"""
        if not response or not response.strip():
            return ""
            
        # Remove markdown code blocks
        response = re.sub(r"^```json\s*", "", response.strip())
        response = re.sub(r"^```\s*", "", response.strip())
        response = re.sub(r"```$", "", response.strip())
        response = response.strip()
        
        # If response doesn't start with {, try to find JSON in it
        if response and not response.startswith('{'):
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                response = json_match.group()
        
        return response.strip()

    def run(self, user_prompt):
        try:
            # Get response from Groq
            response = groq_client.chat(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt
            )
            
            # Debug print
            print(f"\n{self.name} Raw Response:")
            print(f"Length: {len(response)} characters")
            print(f"Preview: {response[:200]}...")
            
            # Clean the response
            cleaned_response = self.clean_response(response)
            
            # If cleaned response is empty, return error
            if not cleaned_response:
                print(f"Warning: Empty response from {self.name}")
                return self.get_error_response()
            
            # Process the response
            return self.process_response(cleaned_response)
            
        except Exception as e:
            print(f"Error in {self.name}.run(): {e}")
            return self.get_error_response()

    def get_error_response(self):
        """Return a default error response for the agent"""
        if self.name == "PlannerAgent":
            return {
                "agents": ["ThreatAgent", "PolicyAgent", "SimulationAgent", "ExecutiveAgent"],
                "reasoning": "Error occurred, using all agents as fallback"
            }
        else:
            return {
                "decision": "REVIEW",
                "risk_score": 50,
                "confidence": 0.5,
                "reason": "Error occurred, defaulting to REVIEW"
            }