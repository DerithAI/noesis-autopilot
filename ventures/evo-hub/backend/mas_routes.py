"""
M-AI-SELF Routes — exposes M-AI-SELF API through EVO-HUB.
Step 1 of 4: Bridge EVO-DASH ↔ M-AI-SELF
"""
from fastapi import APIRouter
from typing import Dict, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/mas", tags=["m-ai-self"])

# Import bridge
try:
    from m_ai_self_bridge import MAISelfBridge
    MAS_AVAILABLE = True
except ImportError:
    MAS_AVAILABLE = False

class ProcessPayload(BaseModel):
    text: str

class BindPayload(BaseModel):
    path: str
    name: Optional[str] = None

@router.get("/health")
async def mas_health() -> Dict:
    """M-AI-SELF health check."""
    if not MAS_AVAILABLE:
        return {"available": False, "error": "M-AI-SELF bridge not installed"}
    bridge = MAISelfBridge()
    return {"available": bridge.is_available(), "details": bridge.health()}

@router.get("/status")
async def mas_status() -> Dict:
    """Full M-AI-SELF system status."""
    if not MAS_AVAILABLE:
        return {"available": False}
    bridge = MAISelfBridge()
    if not bridge.is_available():
        return {"available": False}
    return {"available": True, **bridge.status()}

# ── Memory ──

@router.get("/memory/episodic")
async def mas_episodic() -> Dict:
    if not MAS_AVAILABLE:
        return {"error": "not_available"}
    return MAISelfBridge().get_episodic_memory()

@router.get("/memory/semantic")
async def mas_semantic() -> Dict:
    if not MAS_AVAILABLE:
        return {"error": "not_available"}
    return MAISelfBridge().get_semantic_memory()

@router.get("/memory/search")
async def mas_search(query: str, top_k: int = 5) -> Dict:
    if not MAS_AVAILABLE:
        return {"error": "not_available"}
    return MAISelfBridge().search_semantic_memory(query, top_k)

@router.get("/memory/checkpoints")
async def mas_checkpoints() -> Dict:
    if not MAS_AVAILABLE:
        return {"error": "not_available"}
    return MAISelfBridge().get_checkpoints()

@router.get("/memory/conversation")
async def mas_conversation() -> Dict:
    if not MAS_AVAILABLE:
        return {"error": "not_available"}
    return MAISelfBridge().get_conversation_history()

# ── Project Binding ──

@router.post("/projects/bind")
async def mas_bind_project(payload: BindPayload) -> Dict:
    if not MAS_AVAILABLE:
        return {"error": "not_available"}
    return MAISelfBridge().bind_project(payload.path, payload.name)

@router.get("/projects/active")
async def mas_active_project() -> Dict:
    if not MAS_AVAILABLE:
        return {"error": "not_available"}
    return MAISelfBridge().get_active_project()

@router.get("/projects/list")
async def mas_list_projects() -> Dict:
    if not MAS_AVAILABLE:
        return {"error": "not_available"}
    return MAISelfBridge().list_projects()

@router.post("/projects/refresh")
async def mas_refresh_project(force_full: bool = False) -> Dict:
    if not MAS_AVAILABLE:
        return {"error": "not_available"}
    return MAISelfBridge().refresh_project(force_full)

# ── Worlds ──

@router.get("/worlds")
async def mas_worlds() -> Dict:
    if not MAS_AVAILABLE:
        return {"error": "not_available"}
    return MAISelfBridge().list_worlds()

@router.get("/worlds/active")
async def mas_active_world() -> Dict:
    if not MAS_AVAILABLE:
        return {"error": "not_available"}
    return MAISelfBridge().get_active_world()

# ── Cognitive Loop ──

@router.post("/process")
async def mas_process(payload: ProcessPayload) -> Dict:
    if not MAS_AVAILABLE:
        return {"error": "not_available"}
    return MAISelfBridge().process(payload.text)

# ── Metrics ──

@router.get("/metrics")
async def mas_metrics() -> Dict:
    if not MAS_AVAILABLE:
        return {"error": "not_available"}
    return MAISelfBridge().get_metrics()
