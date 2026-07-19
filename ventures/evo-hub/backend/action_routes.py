"""
Action Routes — real backends for EVO-DASH action buttons.
Używa lokalnych agentów, skilli i narzędzi. Zero API zewnętrznych.
"""
import subprocess
import sys
import json
import os
import time
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

router = APIRouter(prefix="/api", tags=["actions"])

# Simple in-memory rate limiter: max 1 request per 10 seconds per IP per endpoint
_rate_limit_store: Dict[str, float] = {}
RATE_LIMIT_SECONDS = 10

def rate_limit(request: Request):
    """Check rate limit for client IP."""
    client_ip = request.client.host if request.client else "unknown"
    endpoint = request.url.path
    key = f"{client_ip}:{endpoint}"
    now = time.time()
    last = _rate_limit_store.get(key, 0)
    if now - last < RATE_LIMIT_SECONDS:
        raise HTTPException(status_code=429, detail=f"Rate limited. Wait {RATE_LIMIT_SECONDS - int(now - last)}s.")
    _rate_limit_store[key] = now

REPO_ROOT = Path(__file__).parent.parent.parent.parent

class GenerateRequest(BaseModel):
    seed: str = Field(min_length=1, max_length=200)
    model: str = Field(default="qwen2.5:7b", min_length=1, max_length=100)
    stack: str = Field(default="auto", min_length=1, max_length=50)

class CognitiveRequest(BaseModel):
    input: str = Field(min_length=1, max_length=10_000)
    mode: str = Field(default="chat", min_length=1, max_length=50)

class HowlRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2_000)
    frequency: str = Field(default="medium", min_length=1, max_length=50)

@router.post("/action/generate")
async def action_generate(req: GenerateRequest, request: Request) -> Dict:
    rate_limit(request)
    """Trigger Venture-Swarm generation for a new venture."""
    cmd = [
        sys.executable, str(REPO_ROOT / "venture-swarm.py"),
        req.seed,
        "--model", req.model,
        "--deploy"
    ]
    if req.stack != "auto":
        cmd += ["--stack", req.stack]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300,
            cwd=str(REPO_ROOT)
        )
        return {
            "success": result.returncode == 0,
            "seed": req.seed,
            "stdout": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout,
            "stderr": result.stderr[-500:] if result.stderr else "",
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Venture-Swarm timed out after 5min"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/action/tests")
async def action_run_tests(request: Request) -> Dict:
    rate_limit(request)
    """Run all pytest suites across ventures and forge-bot."""
    results = []
    test_targets = [
        ("forge-bot", REPO_ROOT / "forge-bot"),
        ("evo-hub", REPO_ROOT / "ventures" / "evo-hub" / "tests"),
        ("noesis", REPO_ROOT / "tests"),
    ]
    for name, path in test_targets:
        if not path.exists():
            continue
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(path), "-q", "--tb=short"],
                capture_output=True, text=True, timeout=120,
                cwd=str(REPO_ROOT)
            )
            results.append({
                "suite": name,
                "passed": result.returncode == 0,
                "output": result.stdout[-1500:] if len(result.stdout) > 1500 else result.stdout
            })
        except Exception as e:
            results.append({"suite": name, "passed": False, "error": str(e)})
    total_passed = sum(1 for r in results if r.get("passed"))
    return {
        "suites": results,
        "total_passed": total_passed,
        "total_suites": len(results)
    }

@router.post("/action/cognitive")
async def action_cognitive(req: CognitiveRequest, request: Request) -> Dict:
    rate_limit(request)
    """Run EVO Agent cognitive loop via LUMEN or local fallback."""
    try:
        sys.path.insert(0, str(REPO_ROOT / "ventures" / "evo-hub" / "agents"))
        from evo_agent import EVOAgent
        agent = EVOAgent()
        stages = agent.run_loop(req.input)
        return {
            "stages": [{"name": s.get("stage", "unknown"), "status": "ok"} for s in stages],
            "input": req.input,
            "mode": req.mode
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/action/howl")
async def action_howl(req: HowlRequest, request: Request) -> Dict:
    rate_limit(request)
    """Send WOLF howl to pack."""
    try:
        sys.path.insert(0, str(REPO_ROOT / "forge-bot"))
        from wolf_bridge import wolf_howl
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        wolf_howl(req.message, req.frequency)
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        return {"sent": True, "message": req.message, "raw": output}
    except Exception as e:
        return {"sent": False, "error": str(e)}

@router.get("/action/insights")
async def action_insights(request: Request) -> Dict:
    rate_limit(request)
    """Generate NOESIS insights from autopilot_memory.db."""
    try:
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "noesis_insights.py")],
            capture_output=True, text=True, timeout=60,
            cwd=str(REPO_ROOT)
        )
        insights_path = REPO_ROOT / "noesis_insights.md"
        insights_text = insights_path.read_text() if insights_path.exists() else result.stdout
        return {
            "generated": result.returncode == 0,
            "insights": insights_text[:2000] if len(insights_text) > 2000 else insights_text
        }
    except Exception as e:
        return {"generated": False, "error": str(e)}
