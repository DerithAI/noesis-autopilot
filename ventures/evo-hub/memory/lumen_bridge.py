#!/usr/bin/env python3
"""
LUMEN OS Bridge for EVO-HUB
Lightweight HTTP client connecting to LUMEN cognitive API (port 8002).

Requires LUMEN OS running:
    cd C:\Users\Main\SELF-EVOLVING-SYSTEM\m-ai-self
    uvicorn apps.api.main:app --port 8002
"""
import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime

LUMEN_HOST = os.environ.get("LUMEN_HOST", "127.0.0.1:8002")
if ":" not in LUMEN_HOST:
    LUMEN_HOST += ":8002"

class LumenBridge:
    """Bridge to LUMEN OS cognitive engine."""
    
    def __init__(self, host: str = None):
        self.host = host or LUMEN_HOST
        self.base_url = f"http://{self.host}"
        self._available = None
    
    def is_available(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=5)
            self._available = resp.status_code == 200
            return self._available
        except Exception:
            self._available = False
            return False
    
    def cognitive_loop(self, input_text: str, mode: str = "chat") -> Dict:
        """Run 6-stage LUMEN cognitive loop on input."""
        if not self.is_available():
            return {"error": "LUMEN not available", "stages": []}
        try:
            resp = requests.post(
                f"{self.base_url}/api/cognitive/process",
                json={"input": input_text, "mode": mode},
                timeout=30
            )
            return resp.json()
        except Exception as e:
            return {"error": str(e), "stages": []}
    
    def vector_search(self, query: str, limit: int = 5) -> List[Dict]:
        """Semantic search via ChromaDB (nomic-embed-text 768-dim)."""
        if not self.is_available():
            return []
        try:
            resp = requests.post(
                f"{self.base_url}/api/memory/semantic/search",
                json={"query": query, "limit": limit},
                timeout=10
            )
            return resp.json().get("results", [])
        except Exception:
            return []
    
    def store_episode(self, content: str, category: str = "evo_hub", metadata: Dict = None) -> str:
        """Store episodic memory in LUMEN."""
        if not self.is_available():
            return ""
        try:
            resp = requests.post(
                f"{self.base_url}/api/memory/episodic",
                json={"content": content, "category": category, "metadata": metadata or {}},
                timeout=10
            )
            return resp.json().get("id", "")
        except Exception:
            return ""
    
    def agent_run(self, mode: str = "architect", task: str = "", context: Dict = None) -> Dict:
        """Run a LUMEN agent (architect/engineer/critic/synthesizer/memory_keeper)."""
        if not self.is_available():
            return {"error": "LUMEN not available"}
        try:
            resp = requests.post(
                f"{self.base_url}/api/agents/run",
                json={"mode": mode, "task": task, "context": context or {}},
                timeout=60
            )
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_status(self) -> Dict:
        """Get LUMEN system status."""
        if not self.is_available():
            return {"status": "offline"}
        try:
            resp = requests.get(f"{self.base_url}/api/status", timeout=5)
            return resp.json()
        except Exception:
            return {"status": "error"}


if __name__ == "__main__":
    lumen = LumenBridge()
    print("LUMEN Status:", lumen.get_status())
    print("Cognitive loop test:", lumen.cognitive_loop("Test EVO-HUB integration"))
