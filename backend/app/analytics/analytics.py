# analytics/analytics_engine.py
import json
from collections import Counter
from typing import List, Dict, Any
from datetime import datetime, timedelta


class AnalyticsEngine:
    """
    Analytics engine for generating insights from audit logs.
    Handles both old and new database formats.
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_time = None
        self.cache_duration = timedelta(minutes=5)
    
    def generate(self, history: List[Dict]) -> Dict[str, Any]:
        """Generate analytics from history logs."""
        if not history:
            return self._empty_stats()
        
        total_requests = len(history)
        
        decisions = []
        risks = []
        actions = []
        tools = []
        environments = []
        sensitivities = []
        modes = []
        
        critical = 0
        high_risk_events = 0
        avg_confidence = []
        
        for event in history:
            # -----------------------------
            # Extract consensus data
            # -----------------------------
            consensus = {}
            
            # New database format (raw_event is JSON string)
            if event.get("raw_event"):
                try:
                    consensus = json.loads(event["raw_event"])
                except Exception:
                    consensus = {}
            
            # Old format (direct consensus object)
            elif event.get("consensus"):
                consensus = event["consensus"]
            
            # -----------------------------
            # Extract decision
            # -----------------------------
            decision = (
                event.get("decision")
                or consensus.get("final_decision")
                or "UNKNOWN"
            )
            decisions.append(decision)
            
            # -----------------------------
            # Extract risk score
            # -----------------------------
            risk = (
                event.get("risk_score")
                or consensus.get("overall_risk")
                or 0
            )
            # Ensure risk is int
            risk = int(risk)
            risks.append(risk)
            
            if risk >= 70:
                high_risk_events += 1
            
            # -----------------------------
            # Extract confidence
            # -----------------------------
            confidence = (
                event.get("confidence")
                or consensus.get("confidence")
                or 0
            )
            # Ensure confidence is float
            confidence = float(confidence)
            if confidence:
                avg_confidence.append(confidence)
            
            # -----------------------------
            # Extract event data
            # -----------------------------
            event_data = consensus.get("event", {})
            
            action = (
                event.get("action")
                or event_data.get("action")
                or "unknown"
            )
            actions.append(action)
            
            tool = (
                event.get("tool")
                or event_data.get("tool")
                or "unknown"
            )
            tools.append(tool)
            
            environment = (
                event.get("environment")
                or event_data.get("environment")
                or "unknown"
            )
            environments.append(environment)
            
            sensitivity = (
                event.get("sensitivity")
                or event_data.get("sensitivity")
                or "unknown"
            )
            sensitivities.append(sensitivity)
            
            if sensitivity == "critical":
                critical += 1
            
            # -----------------------------
            # Extract mode
            # -----------------------------
            mode = event.get("mode", "unknown")
            modes.append(mode)
        
        # -----------------------------
        # Count distributions
        # -----------------------------
        decision_counter = Counter(decisions)
        action_counter = Counter(actions)
        tool_counter = Counter(tools)
        env_counter = Counter(environments)
        sens_counter = Counter(sensitivities)
        mode_counter = Counter(modes)
        
        # Calculate averages
        avg_risk = round(sum(risks) / len(risks), 2) if risks else 0
        avg_conf = round(sum(avg_confidence) / len(avg_confidence), 2) if avg_confidence else 0
        
        # Get date range
        dates = []
        for event in history:
            timestamp = event.get("timestamp")
            if timestamp:
                try:
                    dates.append(datetime.fromisoformat(timestamp))
                except:
                    pass
        
        date_range = None
        if dates:
            date_range = {
                "first": min(dates).strftime("%Y-%m-%d %H:%M:%S"),
                "last": max(dates).strftime("%Y-%m-%d %H:%M:%S"),
                "days": (max(dates) - min(dates)).days
            }
        
        return {
            "total_requests": total_requests,
            "blocked": decision_counter.get("BLOCK", 0),
            "allowed": decision_counter.get("ALLOW", 0),
            "review": decision_counter.get("REVIEW", 0),
            "average_risk": avg_risk,
            "average_confidence": avg_conf,
            "critical_events": critical,
            "high_risk_events": high_risk_events,
            "top_actions": action_counter.most_common(5),
            "top_tools": tool_counter.most_common(5),
            "top_environments": env_counter.most_common(3),
            "sensitivity_distribution": dict(sens_counter),
            "decision_distribution": dict(decision_counter),
            "mode_distribution": dict(mode_counter),
            "date_range": date_range,
            "timestamp": datetime.now().isoformat()
        }
    
    def _empty_stats(self) -> Dict[str, Any]:
        """Return empty statistics."""
        return {
            "total_requests": 0,
            "blocked": 0,
            "allowed": 0,
            "review": 0,
            "average_risk": 0,
            "average_confidence": 0,
            "critical_events": 0,
            "high_risk_events": 0,
            "top_actions": [],
            "top_tools": [],
            "top_environments": [],
            "sensitivity_distribution": {},
            "decision_distribution": {},
            "mode_distribution": {},
            "date_range": None,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_daily_summary(self, history: List[Dict]) -> Dict[str, Any]:
        """Generate daily summary statistics."""
        if not history:
            return {}
        
        daily_stats = {}
        for event in history:
            timestamp = event.get("timestamp", "")
            date = timestamp[:10] if timestamp else "unknown"
            
            if date not in daily_stats:
                daily_stats[date] = {
                    "date": date,
                    "count": 0,
                    "blocked": 0,
                    "allowed": 0,
                    "review": 0,
                    "risks": []
                }
            
            stats = daily_stats[date]
            stats["count"] += 1
            
            # -----------------------------
            # Extract consensus data
            # -----------------------------
            consensus = {}
            
            if event.get("raw_event"):
                try:
                    consensus = json.loads(event["raw_event"])
                except Exception:
                    consensus = {}
            elif event.get("consensus"):
                consensus = event["consensus"]
            
            # -----------------------------
            # Extract decision
            # -----------------------------
            decision = (
                event.get("decision")
                or consensus.get("final_decision")
                or "UNKNOWN"
            )
            
            # -----------------------------
            # Extract risk
            # -----------------------------
            risk = (
                event.get("risk_score")
                or consensus.get("overall_risk")
                or 0
            )
            risk = int(risk)
            
            if decision == "BLOCK":
                stats["blocked"] += 1
            elif decision == "ALLOW":
                stats["allowed"] += 1
            elif decision == "REVIEW":
                stats["review"] += 1
            
            stats["risks"].append(risk)
        
        # Calculate averages
        for date, stats in daily_stats.items():
            if stats["risks"]:
                stats["average_risk"] = round(sum(stats["risks"]) / len(stats["risks"]), 2)
            else:
                stats["average_risk"] = 0
            del stats["risks"]
        
        sorted_dates = sorted(daily_stats.keys(), reverse=True)[:7]
        return {date: daily_stats[date] for date in sorted_dates}
    
    def generate_trends(self, history: List[Dict]) -> Dict[str, Any]:
        """Generate trend analysis."""
        if not history:
            return {"message": "No data for trend analysis"}
        
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        recent_history = []
        for event in history:
            timestamp = event.get("timestamp")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    if dt >= thirty_days_ago:
                        recent_history.append(event)
                except:
                    pass
        
        if not recent_history:
            return {"message": "Not enough data for trend analysis"}
        
        total = len(recent_history)
        
        # -----------------------------
        # Count blocked events
        # -----------------------------
        blocked = 0
        for event in recent_history:
            decision = event.get("decision")
            
            # If decision not in top level, check raw_event
            if not decision and event.get("raw_event"):
                try:
                    consensus = json.loads(event["raw_event"])
                    decision = consensus.get("final_decision")
                except Exception:
                    pass
            
            if decision == "BLOCK":
                blocked += 1
        
        block_rate = round((blocked / total) * 100, 2) if total > 0 else 0
        
        # -----------------------------
        # Get top actions
        # -----------------------------
        actions = Counter()
        for event in recent_history:
            action = event.get("action", "unknown")
            
            # If action not in top level, check raw_event
            if action == "unknown" and event.get("raw_event"):
                try:
                    consensus = json.loads(event["raw_event"])
                    event_data = consensus.get("event", {})
                    action = event_data.get("action", "unknown")
                except Exception:
                    pass
            
            actions[action] += 1
        
        return {
            "period_days": 30,
            "total_events": total,
            "block_rate": block_rate,
            "blocked_count": blocked,
            "top_actions": actions.most_common(5),
            "trending": "Increasing" if block_rate > 20 else "Stable" if block_rate > 10 else "Decreasing"
        }