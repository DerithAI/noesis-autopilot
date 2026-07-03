"""
M-AI-SELF Memory Adapter — Hybrid memory using M-AI-SELF semantic/episodic stores.
Step 2 of 4: Use M-AI-SELF memory

Priority:
  1. M-AI-SELF semantic search (vector embeddings)
  2. M-AI-SELF episodic memory
  3. Local SQLite fallback
"""
import requests
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional

M_AI_SELF_BASE = "http://127.0.0.1:8002"
LOCAL_DB = Path(__file__).parent.parent.parent.parent / "autopilot_memory.db"

class HybridMemory:
    """Hybrid memory: M-AI-SELF (primary) + SQLite (fallback)."""
    
    def __init__(self):
        self.mas_available = self._check_mas()
    
    def _check_mas(self) -> bool:
        try:
            requests.get(f"{M_AI_SELF_BASE}/health", timeout=2)
            return True
        except Exception:
            return False
    
    # ── Semantic Search (Vector) ──
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search memory using M-AI-SELF semantic search (vector) or local fallback."""
        if self.mas_available:
            try:
                resp = requests.get(
                    f"{M_AI_SELF_BASE}/api/memory/semantic/search",
                    params={"query": query, "top_k": limit},
                    timeout=5
                )
                data = resp.json()
                results = data.get("results", [])
                if results:
                    return [{"source": "mas_semantic", **r} for r in results]
            except Exception:
                pass
        
        # Fallback: local SQLite
        return self._local_search(query, limit)
    
    def _local_search(self, query: str, limit: int) -> List[Dict]:
        if not LOCAL_DB.exists():
            return []
        try:
            conn = sqlite3.connect(str(LOCAL_DB))
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, content, timestamp FROM memory WHERE content LIKE ? ORDER BY timestamp DESC LIMIT ?",
                (f"%{query}%", limit)
            )
            rows = cursor.fetchall()
            return [{"source": "local_sqlite", "id": r[0], "content": r[1], "timestamp": r[2]} for r in rows]
        except Exception:
            return []
    
    # ── Episodic Memory ──
    def get_episodes(self, limit: int = 10) -> List[Dict]:
        """Get episodic memories from M-AI-SELF."""
        if self.mas_available:
            try:
                resp = requests.get(f"{M_AI_SELF_BASE}/api/memory/episodic", timeout=5)
                data = resp.json()
                memories = data.get("memories", [])
                return memories[:limit]
            except Exception:
                pass
        return []
    
    # ── Checkpoints ──
    def get_checkpoints(self, limit: int = 5) -> List[Dict]:
        """Get system checkpoints from M-AI-SELF."""
        if self.mas_available:
            try:
                resp = requests.get(f"{M_AI_SELF_BASE}/api/memory/checkpoints", timeout=5)
                data = resp.json()
                checkpoints = data.get("checkpoints", [])
                return checkpoints[:limit]
            except Exception:
                pass
        return []
    
    # ── Conversation History ──
    def get_conversation(self, limit: int = 20) -> List[Dict]:
        """Get conversation history from M-AI-SELF."""
        if self.mas_available:
            try:
                resp = requests.get(f"{M_AI_SELF_BASE}/api/conversation/history", timeout=5)
                data = resp.json()
                history = data.get("history", [])
                return history[:limit]
            except Exception:
                pass
        return []
    
    # ── Store to local (always works) ──
    def store_local(self, key: str, content: str, category: str = "general") -> bool:
        """Store memory to local SQLite (always available)."""
        try:
            conn = sqlite3.connect(str(LOCAL_DB))
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY,
                    key TEXT,
                    content TEXT,
                    category TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute(
                "INSERT INTO memory (key, content, category) VALUES (?, ?, ?)",
                (key, content, category)
            )
            conn.commit()
            return True
        except Exception:
            return False
    
    # ── Status ──
    def status(self) -> Dict:
        return {
            "mas_available": self.mas_available,
            "local_db": str(LOCAL_DB),
            "local_db_exists": LOCAL_DB.exists(),
            "sources": ["mas_semantic", "mas_episodic", "mas_checkpoints", "local_sqlite"]
        }
