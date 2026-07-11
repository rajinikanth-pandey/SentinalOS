# api/chat.py
from llm.client import groq_client
from typing import Optional, Dict, Any
from datetime import datetime


class ChatService:
    """
    Simple chat service for general Q&A without security orchestration.
    """
    
    SYSTEM_PROMPT = """
You are SentinelOS AI Assistant, a helpful and knowledgeable AI assistant.

Your areas of expertise include:
- Cybersecurity (threat analysis, security best practices, compliance)
- Cloud Computing (AWS, Azure, GCP, Kubernetes, Docker)
- DevOps (CI/CD, automation, infrastructure as code)
- Programming (Python, Go, Rust, JavaScript, etc.)
- Networking (TCP/IP, DNS, load balancing, firewalls)
- Linux (system administration, shell scripting, performance tuning)
- Artificial Intelligence (machine learning, LLMs, prompt engineering)
- General Knowledge (science, technology, history, current events)

Guidelines:
1. Be concise, accurate, and professional
2. Provide practical examples when relevant
3. Acknowledge limitations when appropriate
4. Use markdown formatting for code blocks and lists
5. Prioritize safety and security in all responses
6. If unsure, be honest about your uncertainty

Remember: You are an AI assistant, not a human. Don't pretend to have emotions or personal experiences.
"""

    def __init__(self):
        self.chat_history = []
        self.conversation_id = None
    
    def chat(self, prompt: str, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Process a chat prompt and return a response.
        
        Args:
            prompt: User's question or prompt
            temperature: Response creativity (0.0-1.0)
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Get response from Groq
            response = groq_client.chat(
                system_prompt=self.SYSTEM_PROMPT,
                user_prompt=prompt
            )
            
            return {
                "response": response,
                "temperature": temperature,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_history(self) -> Dict[str, Any]:
        """Get conversation history."""
        return {
            "conversation_id": self.conversation_id,
            "message_count": len(self.chat_history),
            "history": self.chat_history
        }
    
    def clear_history(self) -> Dict[str, Any]:
        """Clear conversation history."""
        self.chat_history = []
        self.conversation_id = None
        return {"message": "Conversation history cleared"}


# Singleton instance
chat_service = ChatService()