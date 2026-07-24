"""
WebSocket routes — real-time updates for EVO-DASH.
Pushes system status, pipeline, ventures, ITDD every 5 seconds.
Also broadcasts venture generation progress.
"""
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Set

router = APIRouter(prefix="/ws", tags=["websocket"])

# Connected WebSocket clients
active_connections: Set[WebSocket] = set()

async def fetch_status() -> Dict:
    import requests
    status = {"evo_hub": True, "lumen": False, "ollama": False, "ventures": 7}
    try:
        requests.get("http://127.0.0.1:8002/health", timeout=2)
        status["lumen"] = True
    except:
        pass
    try:
        requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
        status["ollama"] = True
    except:
        pass
    return status

async def broadcast(message: Dict):
    """Send a message to all connected WebSocket clients."""
    disconnected = set()
    for ws in active_connections:
        try:
            await ws.send_json(message)
        except Exception:
            disconnected.add(ws)
    active_connections.difference_update(disconnected)

@router.websocket("/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            status = await fetch_status()
            await websocket.send_json({
                "type": "status",
                "data": status,
                "timestamp": asyncio.get_event_loop().time()
            })
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        active_connections.discard(websocket)
    except Exception:
        active_connections.discard(websocket)
        await websocket.close()

# Expose broadcast function for action_routes to use
__all__ = ["broadcast"]
