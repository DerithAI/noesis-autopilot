from fastapi import APIRouter
from typing import List, Dict

router = APIRouter(prefix="/api", tags=["dashboard"])

ventures = [
    {"name": "Task priority notifier", "seed": "todo app", "stack": "fastapi + react", "files": 6, "status": "deployed"},
    {"name": "Quiz generator bot", "seed": "discord bot", "stack": "fastapi", "files": 7, "status": "deployed"},
    {"name": "LeadGenTrackerAPI", "seed": "saas api", "stack": "fastapi", "files": 4, "status": "deployed"},
    {"name": "Auto-fill private keys scanner", "seed": "crypto scraper", "stack": "fastapi", "files": 3, "status": "deployed"},
    {"name": "personalized_workout", "seed": "ai assistant", "stack": "fastapi + react", "files": 11, "status": "deployed"},
    {"name": "Personalized Evo Learning Path", "seed": "evo hub", "stack": "fastapi + react", "files": 14, "status": "deployed"},
    {"name": "evo-hub", "seed": "master dashboard", "stack": "fastapi + react + lumen", "files": 28, "status": "live"},
]

@router.get("/ventures")
async def get_ventures() -> List[Dict]:
    return ventures

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
