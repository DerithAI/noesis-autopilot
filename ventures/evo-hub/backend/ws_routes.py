"""
WebSocket routes — real-time updates for EVO-DASH.
Pushes system status, pipeline, ventures, ITDD every 5 seconds.
"""
import asyncio
import json
from fastapi import APIRouter, WebSocket
from typing import Dict

router = APIRouter(prefix="/ws", tags=["websocket"])

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

@router.websocket("/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            status = await fetch_status()
            await websocket.send_json({
                "type": "status",
                "data": status,
                "timestamp": asyncio.get_event_loop().time()
            })
            await asyncio.sleep(5)
    except Exception:
        await websocket.close()
