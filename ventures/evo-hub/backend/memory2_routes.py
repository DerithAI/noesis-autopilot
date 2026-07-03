"""
Hybrid Memory Routes — exposes M-AI-SELF memory through EVO-HUB.
Step 2 of 4: Use M-AI-SELF memory
"""
from fastapi import APIRouter, Query
from typing import Dict, List

router = APIRouter(prefix="/api/memory2", tags=["hybrid-memory"])

try:
    from memory_adapter import HybridMemory
    MEM_AVAILABLE = True
except ImportError:
    MEM_AVAILABLE = False

@router.get("/status")
async def memory_status() -> Dict:
    """Show hybrid memory status (M-AI-SELF + local)."""
    if not MEM_AVAILABLE:
        return {"available": False, "error": "memory_adapter not installed"}
    mem = HybridMemory()
    return {"available": True, **mem.status()}

@router.get("/search")
async def memory_search(query: str = Query(...), limit: int = 5) -> Dict:
    """Semantic search across M-AI-SELF vector memory + local SQLite."""
    if not MEM_AVAILABLE:
        return {"error": "not_available"}
    mem = HybridMemory()
    results = mem.search(query, limit)
    return {
        "query": query,
        "count": len(results),
        "sources": list(set(r.get("source", "unknown") for r in results)),
        "results": results
    }

@router.get("/episodes")
async def memory_episodes(limit: int = 10) -> Dict:
    """Get episodic memories from M-AI-SELF."""
    if not MEM_AVAILABLE:
        return {"error": "not_available"}
    mem = HybridMemory()
    episodes = mem.get_episodes(limit)
    return {"count": len(episodes), "episodes": episodes}

@router.get("/checkpoints")
async def memory_checkpoints(limit: int = 5) -> Dict:
    """Get system checkpoints from M-AI-SELF."""
    if not MEM_AVAILABLE:
        return {"error": "not_available"}
    mem = HybridMemory()
    checkpoints = mem.get_checkpoints(limit)
    return {"count": len(checkpoints), "checkpoints": checkpoints}

@router.get("/conversation")
async def memory_conversation(limit: int = 20) -> Dict:
    """Get conversation history from M-AI-SELF."""
    if not MEM_AVAILABLE:
        return {"error": "not_available"}
    mem = HybridMemory()
    history = mem.get_conversation(limit)
    return {"count": len(history), "history": history}
