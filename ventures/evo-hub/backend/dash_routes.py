from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from pathlib import Path
import subprocess
import sys

router = APIRouter(prefix="/api", tags=["dashboard"])

REPO_ROOT = Path(__file__).parent.parent.parent.parent
VENTURES_DIR = REPO_ROOT / "ventures"

ventures = [
    {"name": "Task priority notifier", "seed": "todo app", "stack": "fastapi + react", "files": 6, "status": "deployed"},
    {"name": "Quiz generator bot", "seed": "discord bot", "stack": "fastapi", "files": 7, "status": "deployed"},
    {"name": "LeadGenTrackerAPI", "seed": "saas api", "stack": "fastapi", "files": 4, "status": "deployed"},
    {"name": "Auto-fill private keys scanner", "seed": "crypto scraper", "stack": "fastapi", "files": 3, "status": "deployed"},
    {"name": "personalized_workout", "seed": "ai assistant", "stack": "fastapi + react", "files": 11, "status": "deployed"},
    {"name": "Personalized Evo Learning Path", "seed": "evo hub", "stack": "fastapi + react", "files": 14, "status": "deployed"},
    {"name": "evo-hub", "seed": "master dashboard", "stack": "fastapi + react + lumen", "files": 28, "status": "live"},
]

def _get_venture_path(name: str) -> Optional[Path]:
    """Find venture directory by name."""
    for v in ventures:
        if v["name"] == name:
            return VENTURES_DIR / name
    return None

def _list_files(path: Path) -> List[Dict]:
    """List files in venture directory."""
    files = []
    for f in path.rglob("*"):
        if f.is_file() and not f.name.startswith(".") and "__pycache__" not in str(f):
            rel = str(f.relative_to(path))
            files.append({
                "path": rel,
                "size": f.stat().st_size,
                "type": f.suffix.lstrip("."),
            })
    return sorted(files, key=lambda x: x["path"])

def _run_tests(path: Path) -> List[Dict]:
    """Run tests for a venture."""
    test_dirs = [d for d in [path / "tests", path / "test"] if d.exists()]
    test_files = list(path.glob("test_*.py"))
    if not test_dirs and not test_files:
        return []
    cmd = [sys.executable, "-m", "pytest"]
    if test_dirs:
        cmd += [str(d) for d in test_dirs]
    if test_files:
        cmd += [str(f) for f in test_files]
    cmd += ["-q", "--tb=short"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=str(path))
        return [{
            "suite": "tests",
            "passed": result.returncode == 0,
            "output": result.stdout[-1500:] if len(result.stdout) > 1500 else result.stdout,
        }]
    except Exception as e:
        return [{"suite": "tests", "passed": False, "output": str(e)}]

@router.get("/ventures")
async def get_ventures() -> List[Dict]:
    return ventures

@router.get("/ventures/{name}")
async def get_venture(name: str) -> Dict:
    """Get detailed info about a specific venture."""
    venture = next((v for v in ventures if v["name"] == name), None)
    if not venture:
        raise HTTPException(status_code=404, detail=f"Venture '{name}' not found")
    
    v_path = _get_venture_path(name)
    file_list = _list_files(v_path) if v_path and v_path.exists() else []
    test_results = _run_tests(v_path) if v_path and v_path.exists() else []
    
    return {
        **venture,
        "file_list": file_list,
        "test_results": test_results,
    }

@router.get("/status")
async def get_system_status() -> Dict:
    import requests
    status = {
        "evo_hub": True,
        "lumen": False,
        "ollama": False,
        "ventures": len(ventures)
    }
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

@router.get("/pipeline")
async def get_pipeline() -> Dict:
    return {
        "steps": ["Observe", "Research", "Architect", "Implement", "Test", "Deploy"],
        "current": "Implement",
        "active_venture": "evo-hub"
    }
