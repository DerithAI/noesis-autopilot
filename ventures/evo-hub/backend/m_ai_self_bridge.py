"""
M-AI-SELF Bridge — connects EVO-HUB to M-AI-SELF API (port 8002).
Step 1 of 4: Bridge EVO-DASH ↔ M-AI-SELF
"""
import httpx
import logging
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

logger = logging.getLogger(__name__)

M_AI_SELF_BASE = "http://127.0.0.1:8002"

class MAISelfBridge:
    """HTTP client for M-AI-SELF API."""
    
    def __init__(self, base_url: str = M_AI_SELF_BASE):
        self.base_url = base_url.rstrip("/")
        self._available: Optional[bool] = None
    
    async def _get(self, path: str, params: dict = None) -> Dict:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{self.base_url}{path}", params=params)
            resp.raise_for_status()
            return resp.json()
    
    async def _post(self, path: str, json_data: dict = None) -> Dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{self.base_url}{path}", json=json_data)
            resp.raise_for_status()
            return resp.json()
    
    def is_available(self) -> bool:
        """Check if M-AI-SELF is running."""
        import requests
        try:
            requests.get(f"{self.base_url}/health", timeout=2)
            self._available = True
            return True
        except Exception:
            self._available = False
            return False
    
    # ── Health & Status ──
    def health(self) -> Dict:
        import requests
        try:
            return requests.get(f"{self.base_url}/health", timeout=2).json()
        except Exception as e:
            return {"error": str(e)}
    
    def status(self) -> Dict:
        import requests
        try:
            return requests.get(f"{self.base_url}/api/status", timeout=3).json()
        except Exception as e:
            return {"error": str(e)}
    
    # ── Memory ──
    def get_episodic_memory(self) -> Dict:
        import requests
        try:
            return requests.get(f"{self.base_url}/api/memory/episodic", timeout=5).json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_semantic_memory(self) -> Dict:
        import requests
        try:
            return requests.get(f"{self.base_url}/api/memory/semantic", timeout=5).json()
        except Exception as e:
            return {"error": str(e)}
    
    def search_semantic_memory(self, query: str, top_k: int = 5) -> Dict:
        import requests
        try:
            return requests.get(
                f"{self.base_url}/api/memory/semantic/search",
                params={"query": query, "top_k": top_k},
                timeout=5
            ).json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_checkpoints(self) -> Dict:
        import requests
        try:
            return requests.get(f"{self.base_url}/api/memory/checkpoints", timeout=5).json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_conversation_history(self) -> Dict:
        import requests
        try:
            return requests.get(f"{self.base_url}/api/conversation/history", timeout=5).json()
        except Exception as e:
            return {"error": str(e)}
    
    # ── Project Binding ──
    def bind_project(self, path: str, name: Optional[str] = None) -> Dict:
        import requests
        try:
            payload = {"path": path}
            if name:
                payload["name"] = name
            return requests.post(
                f"{self.base_url}/projects/bind",
                json=payload,
                timeout=30
            ).json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_active_project(self) -> Dict:
        import requests
        try:
            return requests.get(f"{self.base_url}/projects/active", timeout=5).json()
        except Exception as e:
            return {"error": str(e)}
    
    def list_projects(self) -> Dict:
        import requests
        try:
            return requests.get(f"{self.base_url}/projects/list", timeout=5).json()
        except Exception as e:
            return {"error": str(e)}
    
    def refresh_project(self, force_full: bool = False) -> Dict:
        import requests
        try:
            return requests.post(
                f"{self.base_url}/projects/refresh",
                params={"force_full": force_full},
                timeout=30
            ).json()
        except Exception as e:
            return {"error": str(e)}
    
    # ── Worlds ──
    def list_worlds(self) -> Dict:
        import requests
        try:
            return requests.get(f"{self.base_url}/worlds", timeout=5).json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_active_world(self) -> Dict:
        import requests
        try:
            return requests.get(f"{self.base_url}/worlds/active", timeout=5).json()
        except Exception as e:
            return {"error": str(e)}
    
    # ── Metrics ──
    def get_metrics(self) -> Dict:
        import requests
        try:
            return requests.get(f"{self.base_url}/api/metrics", timeout=5).json()
        except Exception as e:
            return {"error": str(e)}
    
    # ── Process (cognitive loop) ──
    def process(self, text: str) -> Dict:
        import requests
        try:
            return requests.post(
                f"{self.base_url}/process",
                json={"text": text},
                timeout=60
            ).json()
        except Exception as e:
            return {"error": str(e)}
