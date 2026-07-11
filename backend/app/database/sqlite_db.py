# database/sqlite_db.py
import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class SentinelDB:
    """
    SQLite database manager for SentinelOS.
    Handles connection, table creation, and basic operations.
    """
    
    def __init__(self, db_path: str = "database/audit.db"):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        
        # Ensure the database directory exists
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Create connection
        self.connection = sqlite3.connect(
            db_path,
            check_same_thread=False,
            timeout=10
        )
        
        # Enable foreign keys
        self.connection.execute("PRAGMA foreign_keys = ON")
        
        # Row factory for dict-like access
        self.connection.row_factory = sqlite3.Row
        
        # Remove shared cursor - each operation creates its own
        self.cursor = None
        
        # Create tables
        self.create_tables()
        
        print(f"📁 SQLite Database initialized: {db_path}")

    def create_tables(self):
        """Create all necessary tables if they don't exist."""
        # Create a local cursor for this operation
        cursor = self.connection.cursor()
        
        try:
            # Audit logs table with all columns
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_id TEXT UNIQUE,
                timestamp TEXT NOT NULL,
                prompt TEXT NOT NULL,
                action TEXT,
                tool TEXT,
                environment TEXT,
                sensitivity TEXT,
                decision TEXT NOT NULL,
                risk_score INTEGER,
                confidence REAL,
                summary TEXT,
                mode TEXT,
                user_id TEXT,
                session_id TEXT,
                chat_response TEXT,
                raw_event TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Agent results table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_id TEXT,
                agent_name TEXT NOT NULL,
                decision TEXT NOT NULL,
                risk_score INTEGER,
                confidence REAL,
                reason TEXT,
                FOREIGN KEY (log_id) REFERENCES audit_logs(log_id)
            )
            """)
            
            # Violations table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_id TEXT,
                violation_type TEXT NOT NULL,
                description TEXT NOT NULL,
                severity TEXT,
                FOREIGN KEY (log_id) REFERENCES audit_logs(log_id)
            )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_decision ON audit_logs(decision)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_environment ON audit_logs(environment)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_mode ON audit_logs(mode)")
            
            self.connection.commit()
            print("✅ Database tables created successfully")
            
        except sqlite3.Error as e:
            print(f"❌ Error creating tables: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a SELECT query and return results as dicts."""
        cursor = None
        try:
            # Create a new cursor for each query
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except sqlite3.Error as e:
            print(f"❌ Query execution error: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def execute_write(self, query: str, params: tuple = ()) -> Optional[int]:
        """Execute an INSERT/UPDATE/DELETE query and return last row ID."""
        cursor = None
        try:
            # Create a new cursor for each write operation
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            last_id = cursor.lastrowid
            return last_id
        except sqlite3.Error as e:
            print(f"❌ Write operation error: {e}")
            self.connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()

    def get_by_id(self, log_id: str) -> Optional[Dict]:
        """Get a specific log entry by its ID."""
        query = "SELECT * FROM audit_logs WHERE log_id = ?"
        results = self.execute_query(query, (log_id,))
        return results[0] if results else None

    def get_history(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get audit history with pagination."""
        query = """
        SELECT * FROM audit_logs 
        ORDER BY id DESC 
        LIMIT ? OFFSET ?
        """
        return self.execute_query(query, (limit, offset))

    def get_by_decision(self, decision: str, limit: int = 100) -> List[Dict]:
        """Get logs filtered by decision."""
        query = """
        SELECT * FROM audit_logs 
        WHERE decision = ? 
        ORDER BY id DESC 
        LIMIT ?
        """
        return self.execute_query(query, (decision.upper(), limit))

    def get_by_environment(self, environment: str, limit: int = 100) -> List[Dict]:
        """Get logs filtered by environment."""
        query = """
        SELECT * FROM audit_logs 
        WHERE environment = ? 
        ORDER BY id DESC 
        LIMIT ?
        """
        return self.execute_query(query, (environment.lower(), limit))

    def get_by_mode(self, mode: str, limit: int = 100) -> List[Dict]:
        """Get logs filtered by mode."""
        query = """
        SELECT * FROM audit_logs 
        WHERE mode = ? 
        ORDER BY id DESC 
        LIMIT ?
        """
        return self.execute_query(query, (mode.lower(), limit))

    def get_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get logs within a date range."""
        query = """
        SELECT * FROM audit_logs 
        WHERE DATE(timestamp) BETWEEN ? AND ?
        ORDER BY id DESC
        """
        return self.execute_query(query, (start_date, end_date))

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        # Total count
        total = self.execute_query("SELECT COUNT(*) as count FROM audit_logs")
        total_count = total[0]['count'] if total else 0
        
        # Decision distribution
        decisions = self.execute_query("""
        SELECT decision, COUNT(*) as count 
        FROM audit_logs 
        GROUP BY decision
        """)
        
        # Average risk score
        avg_risk = self.execute_query("""
        SELECT AVG(risk_score) as avg_risk 
        FROM audit_logs 
        WHERE risk_score IS NOT NULL
        """)
        
        # Environment distribution
        environments = self.execute_query("""
        SELECT environment, COUNT(*) as count 
        FROM audit_logs 
        GROUP BY environment
        """)
        
        # Mode distribution
        modes = self.execute_query("""
        SELECT mode, COUNT(*) as count 
        FROM audit_logs 
        GROUP BY mode
        """)
        
        return {
            "total_entries": total_count,
            "decision_distribution": {row['decision']: row['count'] for row in decisions},
            "average_risk_score": round(avg_risk[0]['avg_risk'], 2) if avg_risk and avg_risk[0]['avg_risk'] else 0,
            "environment_distribution": {row['environment']: row['count'] for row in environments},
            "mode_distribution": {row['mode']: row['count'] for row in modes} if modes else {},
            "database_path": self.db_path
        }

    def clear_all(self) -> bool:
        """Clear all data from tables."""
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM agent_results")
            cursor.execute("DELETE FROM violations")
            cursor.execute("DELETE FROM audit_logs")
            self.connection.commit()
            print("🗑️ All data cleared from database")
            return True
        except sqlite3.Error as e:
            print(f"❌ Error clearing database: {e}")
            self.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def vacuum(self):
        """Optimize the database."""
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute("VACUUM")
            self.connection.commit()
            print("✅ Database optimized")
        except sqlite3.Error as e:
            print(f"❌ Error optimizing database: {e}")
        finally:
            if cursor:
                cursor.close()

    def close(self):
        """Close the database connection."""
        self.connection.close()
        print("🔒 Database connection closed")


# Singleton instance
db = SentinelDB()