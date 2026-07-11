# orchestrator/orchestrator.py (updated)
import json
from typing import Dict, List, Any, Optional
from agents.planner_agent import PlannerAgent
from agents.threat_agent import ThreatAgent
from agents.policy_agent import PolicyAgent
from agents.simulation_agent import SimulationAgent
from agents.executive_agent import ExecutiveAgent
from consensus.consensus_engine import ConsensusEngine
from database.logger import AuditLogger
from parser.event_parser import EventParser
from rules.risk_engine import RiskEngine
from schemas.security_event import SecurityEvent


class SentinelOrchestrator:

    def __init__(self, use_mock_parser: bool = False, rules_config: Optional[str] = None):
        self.planner = PlannerAgent()
        self.consensus = ConsensusEngine()
        self.logger = AuditLogger()
        self.parser = EventParser(use_mock=use_mock_parser)
        self.risk_engine = RiskEngine(config_path=rules_config)  # Add rule engine
        
        self.available_agents = {
            "ThreatAgent": ThreatAgent(),
            "PolicyAgent": PolicyAgent(),
            "SimulationAgent": SimulationAgent(),
            "ExecutiveAgent": ExecutiveAgent()
        }
        
        print("🛡️ SentinelOS Orchestrator initialized")
        print(f"   • {len(self.available_agents)} AI Agents loaded")
        print(f"   • Rule Engine active with {len(self.risk_engine.rules)} rules")

    def select_agents(self, event: SecurityEvent) -> List[str]:
        """Select agents based on structured event"""
        prompt = self._event_to_prompt(event)
        planner_result = self.planner.run(prompt)
        agents = planner_result.get("agents", [])
        
        # Add intelligent selection based on event type
        if event.requires_approval or event.is_critical():
            if "ExecutiveAgent" not in agents:
                agents.append("ExecutiveAgent")
        
        # Always include PolicyAgent for policy compliance
        if "PolicyAgent" not in agents:
            agents.append("PolicyAgent")
        
        print("\n========== PLANNER ==========")
        print(f"Event: {event.action} ({event.environment})")
        print(f"Selected Agents: {agents}")
        
        return agents

    def run_agents(self, event: SecurityEvent, selected_agents: List[str]) -> List[Dict]:
        """Run selected agents with the structured event"""
        results = []
        prompt = self._event_to_prompt(event)
        
        print("\n========== RUNNING AGENTS ==========")
        
        for agent_name in selected_agents:
            agent = self.available_agents.get(agent_name)
            
            if agent is None:
                print(f"⚠️ {agent_name} not found.")
                continue
            
            print(f"\n🤖 Running {agent_name}...")
            
            try:
                result = agent.run(prompt)
                if isinstance(result, dict):
                    result["agent_name"] = agent_name
                    # Add event context
                    result["event_summary"] = {
                        "action": event.action,
                        "resource": event.resource,
                        "environment": event.environment,
                        "sensitivity": event.sensitivity
                    }
                print(f"✅ {agent_name} completed")
                results.append(result)
            except Exception as e:
                print(f"❌ {agent_name} failed: {e}")
                results.append({
                    "agent_name": agent_name,
                    "decision": "REVIEW",
                    "risk_score": 50,
                    "confidence": 0.5,
                    "error": str(e),
                    "reason": f"Agent execution failed: {str(e)}"
                })
        
        return results

    def analyze(self, prompt: str) -> Dict[str, Any]:
        """Main analysis pipeline with rule engine integration"""
        print("\n" + "="*70)
        print("🛡️ SentinelOS Security Analysis Started")
        print("="*70)
        
        print(f"\n📝 User Request: {prompt}")
        
        # Step 1: Parse prompt into SecurityEvent
        print("\n🔍 Step 1: Parsing security event...")
        event = self.parser.parse(prompt)
        print(f"✅ Event parsed: {event.action} ({event.environment})")
        print(f"   📊 Risk Level: {event.get_risk_level()}")
        print(f"   🔒 Requires Approval: {event.requires_approval}")
        
        # Step 2: Run Rule Engine
        print("\n⚖️ Step 2: Running Rule Engine...")
        rule_result = self.risk_engine.calculate(event.model_dump())
        print(f"   📊 Rule Score: {rule_result['rule_risk_score']}/100")
        print(f"   ⚖️ Rule Decision: {rule_result['rule_decision']}")
        print(f"   📋 Reasons: {len(rule_result['rule_reasons'])} factors")
        
        # Step 3: Select AI agents
        print("\n🤖 Step 3: Selecting AI agents...")
        selected_agents = self.select_agents(event)
        
        # Step 4: Run AI agents
        print("\n🤖 Step 4: Running AI agents...")
        agent_results = self.run_agents(event, selected_agents)
        
        # Step 5: Add rule engine result to agent results
        # This makes the rule engine an "expert" in the consensus process
        rule_agent_result = {
            "agent_name": "RuleEngine",
            "decision": rule_result["rule_decision"],
            "risk_score": rule_result["rule_risk_score"],
            "confidence": 0.95,  # Rule engine is deterministic, high confidence
            "reason": "; ".join(rule_result["rule_reasons"]),
            "matched_rules": rule_result.get("matched_rules", []),
            "is_deterministic": True
        }
        agent_results.append(rule_agent_result)
        
        print("\n========== AGENT RESULTS ==========")
        for result in agent_results:
            print(f"   🤖 {result.get('agent_name', 'Unknown')}: "
                  f"{result.get('decision', 'UNKNOWN')} "
                  f"(Risk: {result.get('risk_score', 0)})")
        
        # Step 6: Get consensus decision
        print("\n⚖️ Step 6: Running Consensus Engine...")
        final_response = self.consensus.decide(agent_results)
        print(f"   📊 Consensus Score: {final_response.get('overall_risk', 0)}")
        print(f"   ⚖️ Final Decision: {final_response.get('final_decision', 'UNKNOWN')}")
        
        # Step 7: Log everything
        print("\n📋 Step 7: Logging results...")
        self.logger.log(
            prompt=prompt,
            planner=selected_agents,
            agent_results=agent_results,
            consensus=final_response,
            event=event.model_dump(),
            metadata={
                "rule_result": rule_result,
                "analysis_timestamp": __import__('datetime').datetime.now().isoformat()
            }
        )
        
        print("\n" + "="*70)
        print("✅ Analysis Completed")
        print(f"   Final Decision: {final_response.get('final_decision', 'UNKNOWN')}")
        print(f"   Risk Score: {final_response.get('overall_risk', 0)}/100")
        print("="*70 + "\n")
        
        # Add event and rule info to response
        final_response["event"] = event.model_dump()
        final_response["rule_result"] = rule_result
        
        return final_response

    def _event_to_prompt(self, event: SecurityEvent) -> str:
        """Convert SecurityEvent back to a prompt for agents"""
        prompt = f"Action: {event.action}\n"
        prompt += f"Resource: {event.resource}\n"
        prompt += f"Tool: {event.tool}\n"
        prompt += f"Environment: {event.environment}\n"
        prompt += f"Sensitivity: {event.sensitivity}\n"
        prompt += f"Actor: {event.actor} ({event.actor_type})\n"
        
        if event.context:
            prompt += f"Context: {json.dumps(event.context)}\n"
        
        return prompt