"""
JARVIS Memory — Experience capsules, persistent storage.
"""
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class MemoryStore:
    """SQLite-based memory for Jarvis."""
    
    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS capsules (
                id TEXT PRIMARY KEY,
                capsule_time TEXT,
                capsule_signal TEXT,
                capsule_decision TEXT,
                capsule_action TEXT,
                capsule_check TEXT,
                calm REAL,
                seed_version TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS seed_history (
                history_time TEXT,
                version TEXT,
                changes TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def save_capsule(self, capsule: Dict) -> bool:
        """Save experience capsule to database."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO capsules 
                (id, capsule_time, capsule_signal, capsule_decision, capsule_action, capsule_check, calm, seed_version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                capsule.get("id"),
                capsule.get("time"),
                json.dumps(capsule.get("signal", {})),
                json.dumps(capsule.get("decision", {})),
                json.dumps(capsule.get("action", {})),
                json.dumps(capsule.get("check", {})),
                capsule.get("calm", 0.5),
                capsule.get("seed_version", "1.0"),
            ))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_capsules(self, limit: int = 10, calm_below: float = None) -> List[Dict]:
        """Retrieve recent capsules."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM capsules ORDER BY capsule_time DESC LIMIT ?"
        params = [limit]
        
        if calm_below is not None:
            query = "SELECT * FROM capsules WHERE calm < ? ORDER BY capsule_time DESC LIMIT ?"
            params = [calm_below, limit]
        
        cursor.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
    
    def get_stats(self) -> Dict:
        """Get memory statistics."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM capsules")
        count = cursor.fetchone()[0]
        cursor.execute("SELECT AVG(calm) FROM capsules")
        avg_calm = cursor.fetchone()[0] or 0.5
        conn.close()
        
        return {
            "total_capsules": count,
            "average_calm": round(avg_calm, 3),
            "db_path": str(self.db_path),
        }
