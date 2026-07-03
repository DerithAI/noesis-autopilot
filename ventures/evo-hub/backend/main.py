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

import os

# CORS whitelist — never use ["*"] in production
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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

# Import dashboard routes
try:
    from dash_routes import router as dash_router
    app.include_router(dash_router)
except ImportError:
    pass

# Import action routes (real buttons)
try:
    from action_routes import router as action_router
    app.include_router(action_router)
except ImportError:
    pass

# Import ITDD routes (compliance scoreboard)
try:
    from itdd_routes import router as itdd_router
    app.include_router(itdd_router)
except ImportError:
    pass

# Import WebSocket routes (real-time updates)
try:
    from ws_routes import router as ws_router
    app.include_router(ws_router)
except ImportError:
    pass

# Import Cognitive Council routes (SUPERPOWERS L3)
try:
    from council_routes import router as council_router
    app.include_router(council_router)
except ImportError:
    pass

# Import M-AI-SELF Bridge routes (Step 1/4)
try:
    from mas_routes import router as mas_router
    app.include_router(mas_router)
except ImportError:
    pass

# Import Hybrid Memory routes (Step 2/4)
try:
    from memory2_routes import router as memory2_router
    app.include_router(memory2_router)
except ImportError:
    pass

# Import OMEGA Bridge routes (Step 4/4)
try:
    from omega_routes import router as omega_router
    app.include_router(omega_router)
except ImportError:
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
