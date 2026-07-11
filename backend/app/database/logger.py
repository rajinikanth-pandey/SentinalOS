# database/logger.py
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib
import threading

from database.models import AuditModel


class AuditLogger:
    """
    Thread-safe audit logger for SentinelOS using SQLite.
    Logs all security events, agent decisions, and consensus results.
    """
    
    def __init__(self, use_sqlite: bool = True):
        self.use_sqlite = use_sqlite
        self._lock = threading.Lock()
        
        if use_sqlite:
            print("📁 Audit Logger initialized with SQLite backend")
        else:
            print("📁 Audit Logger initialized with JSON backend (fallback)")
    
    def log(self, prompt: str, planner: List[str], 
            agent_results: List[Dict], consensus: Dict, 
            event: Optional[Dict] = None,
            metadata: Optional[Dict] = None) -> Optional[str]:
        """
        Log the complete analysis pipeline results.
        """
        # Generate unique log ID
        log_id = self._generate_log_id(prompt)
        
        # Prepare record for database
        record = {
            'log_id': log_id,
            'timestamp': datetime.now().isoformat(),
            'prompt': prompt,
            'action': event.get('action', 'unknown') if event else 'unknown',
            'tool': event.get('tool', 'unknown') if event else 'unknown',
            'environment': event.get('environment', 'development') if event else 'development',
            'sensitivity': event.get('sensitivity', 'low') if event else 'low',
            'decision': consensus.get('final_decision', 'REVIEW'),
            'risk_score': consensus.get('overall_risk', 0),
            'confidence': consensus.get('confidence', 0.5),
            'summary': consensus.get('summary', ''),
            'mode': metadata.get('mode', 'unknown') if metadata else 'unknown',
            'user_id': metadata.get('user_id', 'anonymous') if metadata else 'anonymous',
            'session_id': metadata.get('session_id', 'unknown') if metadata else 'unknown',
            'chat_response': metadata.get('chat_response', '') if metadata else '',
            'raw_analysis': {
                'planner': planner,
                'event': event,
                'metadata': metadata,
                'agent_results': agent_results,
                'consensus': consensus
            },
            'agent_results': agent_results,
            'violations': []
        }
        
        # Extract violations from agent results
        for result in agent_results:
            if 'violations' in result:
                for violation in result['violations']:
                    record['violations'].append({
                        'type': 'policy',
                        'description': violation,
                        'severity': 'high' if 'BLOCK' in result.get('decision', '') else 'medium'
                    })
        
        # Print to console
        self._print_log_entry(record)
        
        # Save to database
        if self.use_sqlite:
            try:
                result = AuditModel.insert(record)
                if result:
                    print(f"✅ Log saved to SQLite: {result}")
                    return result
                else:
                    print("❌ Failed to save to SQLite")
                    return None
            except Exception as e:
                print(f"❌ Error saving to SQLite: {e}")
                import traceback
                traceback.print_exc()
                return None
        else:
            self._save_json_fallback(record)
            return log_id
    
    def _generate_log_id(self, prompt: str) -> str:
        """Generate a unique log ID."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
        return f"LOG-{timestamp}-{prompt_hash}"
    
    def _print_log_entry(self, record: Dict):
        """Print a formatted log entry to console."""
        print("\n" + "="*70)
        print("📋 AUDIT LOG ENTRY")
        print("="*70)
        print(f"🆔 Log ID: {record['log_id']}")
        print(f"🕐 Timestamp: {record['timestamp']}")
        print(f"📝 Prompt: {record['prompt'][:100]}..." if len(record['prompt']) > 100 else f"📝 Prompt: {record['prompt']}")
        print(f"⚖️ Decision: {record['decision']}")
        print(f"📊 Risk Score: {record['risk_score']}/100")
        print(f"📈 Confidence: {record['confidence']:.2f}")
        print(f"🏷️ Environment: {record['environment']}")
        print(f"🔒 Sensitivity: {record['sensitivity']}")
        print("="*70 + "\n")
    
    def _save_json_fallback(self, record: Dict):
        """Save to JSON file as fallback."""
        import json
        from pathlib import Path
        
        json_path = Path("logs") / "audit_log_fallback.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = [logs]
            else:
                logs = []
            
            logs.append(record)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"📁 Log saved to JSON fallback: {json_path}")
        except Exception as e:
            print(f"❌ Failed to save JSON fallback: {e}")
    
    def get_logs(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get logs from database."""
        if self.use_sqlite:
            return AuditModel.get_all(limit, offset)
        else:
            return self._read_json_logs()
    
    def get_log_by_id(self, log_id: str) -> Optional[Dict]:
        """Get a specific log by ID."""
        if self.use_sqlite:
            return AuditModel.get_by_id(log_id)
        else:
            logs = self._read_json_logs()
            for log in logs:
                if log.get('log_id') == log_id:
                    return log
            return None
    
    def get_stats(self) -> Dict:
        """Get statistics."""
        if self.use_sqlite:
            return AuditModel.get_stats()
        else:
            logs = self._read_json_logs()
            return {
                "total_entries": len(logs),
                "database_type": "JSON fallback"
            }
    
    def _read_json_logs(self) -> List[Dict]:
        """Read logs from JSON fallback."""
        import json
        from pathlib import Path
        
        json_path = Path("logs") / "audit_log_fallback.json"
        if not json_path.exists():
            return []
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return [data]
        except:
            return []
    
    def history(self, limit: int = 100) -> List[Dict]:
        """Get history as dicts (for API compatibility)."""
        return self.get_logs(limit)
    
    def clear_logs(self, confirm: bool = False) -> bool:
        """Clear all logs."""
        if not confirm:
            print("⚠️ Use confirm=True to clear all logs")
            return False
        
        if self.use_sqlite:
            from database.sqlite_db import db
            return db.clear_all()
        else:
            print("JSON logs cleared")
            return True