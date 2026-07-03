from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import sys
from pathlib import Path

# Add parent to path for memory bridge
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from memory.lumen_bridge import LumenBridge
    LUMEN_AVAILABLE = True
except ImportError:
    LUMEN_AVAILABLE = False

app = FastAPI(title="EVO-HUB API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    lumen_connected: bool
    version: str

class CognitiveRequest(BaseModel):
    input: str
    mode: str = "chat"

class CognitiveResponse(BaseModel):
    stages: List[Dict]
    lumen_available: bool

@app.get("/health", response_model=HealthResponse)
async def health():
    lumen = LumenBridge() if LUMEN_AVAILABLE else None
    return {
        "status": "healthy",
        "lumen_connected": lumen.is_available() if lumen else False,
        "version": "1.0.0"
    }

@app.post("/cognitive/loop", response_model=CognitiveResponse)
async def cognitive_loop(req: CognitiveRequest):
    if not LUMEN_AVAILABLE:
        return {"stages": [], "lumen_available": False}
    lumen = LumenBridge()
    result = lumen.cognitive_loop(req.input, req.mode)
    return {"stages": result.get("stages", []), "lumen_available": True}

@app.get("/memory/search")
async def memory_search(query: str, limit: int = 5):
    if not LUMEN_AVAILABLE:
        return {"results": [], "lumen_available": False}
    lumen = LumenBridge()
    results = lumen.vector_search(query, limit=limit)
    return {"results": results, "lumen_available": True}

@app.get("/agents/status")
async def agents_status():
    if not LUMEN_AVAILABLE:
        return {"status": "lumen_not_available"}
    lumen = LumenBridge()
    return lumen.get_status()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
