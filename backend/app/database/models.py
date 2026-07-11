# database/models.py
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from database.sqlite_db import db


class AuditModel:
    """
    Model for interacting with the audit_logs table.
    """
    
    @staticmethod
    def insert(record: Dict[str, Any]) -> Optional[str]:
        """Insert a new audit record into the database."""
        # Generate log_id if not provided
        if 'log_id' not in record:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            prompt_hash = hash(record.get('prompt', '')) % 1000000
            log_id = f"LOG-{timestamp}-{prompt_hash:06d}"
        else:
            log_id = record['log_id']
        
        # Prepare data with defaults
        data = {
            'log_id': log_id,
            'timestamp': record.get('timestamp', datetime.now().isoformat()),
            'prompt': record.get('prompt', ''),
            'action': record.get('action', 'unknown'),
            'tool': record.get('tool', 'unknown'),
            'environment': record.get('environment', 'development'),
            'sensitivity': record.get('sensitivity', 'low'),
            'decision': record.get('decision', 'REVIEW'),
            'risk_score': int(record.get('risk_score', 0)),
            'confidence': float(record.get('confidence', 0.5)),
            'summary': record.get('summary', ''),
            'mode': record.get('mode', 'unknown'),
            'user_id': record.get('user_id', 'anonymous'),
            'session_id': record.get('session_id', 'unknown'),
            'chat_response': record.get('chat_response', ''),
            'raw_event': json.dumps(record.get('raw_analysis', {}))
        }
        
        query = """
        INSERT INTO audit_logs (
            log_id, timestamp, prompt, action, tool, 
            environment, sensitivity, decision, risk_score, 
            confidence, summary, mode, user_id, 
            session_id, chat_response, raw_event
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            data['log_id'],
            data['timestamp'],
            data['prompt'],
            data['action'],
            data['tool'],
            data['environment'],
            data['sensitivity'],
            data['decision'],
            data['risk_score'],
            data['confidence'],
            data['summary'],
            data['mode'],
            data['user_id'],
            data['session_id'],
            data['chat_response'],
            data['raw_event']
        )
        
        result = db.execute_write(query, params)
        
        if result:
            # Insert agent results if provided
            if 'agent_results' in record and record['agent_results']:
                for agent_result in record['agent_results']:
                    AgentResultModel.insert(log_id, agent_result)
            
            # Insert violations if provided
            if 'violations' in record and record['violations']:
                for violation in record['violations']:
                    ViolationModel.insert(log_id, violation)
            
            return log_id
        
        return None
    
    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all audit logs with pagination."""
        return db.get_history(limit, offset)
    
    @staticmethod
    def get_by_id(log_id: str) -> Optional[Dict]:
        """Get a specific audit log by ID."""
        return db.get_by_id(log_id)
    
    @staticmethod
    def get_by_decision(decision: str, limit: int = 100) -> List[Dict]:
        """Get logs by decision."""
        return db.get_by_decision(decision, limit)
    
    @staticmethod
    def get_by_environment(environment: str, limit: int = 100) -> List[Dict]:
        """Get logs by environment."""
        return db.get_by_environment(environment, limit)
    
    @staticmethod
    def get_by_mode(mode: str, limit: int = 100) -> List[Dict]:
        """Get logs by mode."""
        return db.get_by_mode(mode, limit)
    
    @staticmethod
    def get_date_range(start_date: str, end_date: str) -> List[Dict]:
        """Get logs within a date range."""
        return db.get_date_range(start_date, end_date)
    
    @staticmethod
    def get_stats() -> Dict:
        """Get database statistics."""
        return db.get_stats()
    
    @staticmethod
    def get_recent(limit: int = 10) -> List[Dict]:
        """Get the most recent logs."""
        return db.get_history(limit, 0)
    
    @staticmethod
    def search(query: str) -> List[Dict]:
        """Search logs by prompt content."""
        search_query = """
        SELECT * FROM audit_logs 
        WHERE prompt LIKE ? 
        OR action LIKE ? 
        OR tool LIKE ?
        ORDER BY id DESC
        LIMIT 100
        """
        search_term = f"%{query}%"
        return db.execute_query(search_query, (search_term, search_term, search_term))


class AgentResultModel:
    """Model for agent results (linked to audit_logs)."""
    
    @staticmethod
    def insert(log_id: str, result: Dict[str, Any]) -> Optional[int]:
        """Insert an agent result."""
        query = """
        INSERT INTO agent_results (
            log_id, agent_name, decision, risk_score, confidence, reason
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        params = (
            log_id,
            result.get('agent_name', 'Unknown'),
            result.get('decision', 'REVIEW'),
            result.get('risk_score', 0),
            result.get('confidence', 0.5),
            result.get('reason', '')
        )
        
        return db.execute_write(query, params)
    
    @staticmethod
    def get_by_log_id(log_id: str) -> List[Dict]:
        """Get all agent results for a specific log."""
        query = "SELECT * FROM agent_results WHERE log_id = ?"
        return db.execute_query(query, (log_id,))


class ViolationModel:
    """Model for violations (linked to audit_logs)."""
    
    @staticmethod
    def insert(log_id: str, violation: Dict[str, Any]) -> Optional[int]:
        """Insert a violation."""
        query = """
        INSERT INTO violations (
            log_id, violation_type, description, severity
        )
        VALUES (?, ?, ?, ?)
        """
        
        params = (
            log_id,
            violation.get('type', 'policy'),
            violation.get('description', ''),
            violation.get('severity', 'medium')
        )
        
        return db.execute_write(query, params)
    
    @staticmethod
    def get_by_log_id(log_id: str) -> List[Dict]:
        """Get all violations for a specific log."""
        query = "SELECT * FROM violations WHERE log_id = ?"
        return db.execute_query(query, (log_id,))