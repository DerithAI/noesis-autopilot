"""
Cognitive Council API — Standalone council deliberation module.
Exposes SUPERPOWERS L3 Council Pattern as a service.
"""
import sys
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List, Optional

router = APIRouter(prefix="/api/council", tags=["council"])

# Add agents path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))

try:
    from evo_agent import EVOAgent
    EVO_AVAILABLE = True
except ImportError:
    EVO_AVAILABLE = False

class DeliberateRequest(BaseModel):
    decision: str
    context: Optional[str] = ""
    require_unanimous: bool = False

class VoiceResult(BaseModel):
    role: str
    recommendation: str
    confidence: int
    reasoning: str

class DeliberateResponse(BaseModel):
    recommendation: str
    confidence: int
    unanimous: bool
    voices: List[VoiceResult]
    context: str

@router.post("/deliberate", response_model=DeliberateResponse)
async def council_deliberate(req: DeliberateRequest) -> Dict:
    """Run 4-voice Council Pattern deliberation on a decision.
    
    SUPERPOWERS L3: Multi-Perspective Analysis
    """
    if not EVO_AVAILABLE:
        return {
            "recommendation": "unavailable",
            "confidence": 0,
            "unanimous": False,
            "voices": [],
            "context": "EVO Agent not available"
        }
    
    agent = EVOAgent()
    voices = agent.council_deliberate(req.decision, {"context": req.context})
    synthesis = agent.council_synthesize(voices)
    
    # If unanimous required and not unanimous, override to "discuss"
    final_rec = synthesis["recommendation"]
    if req.require_unanimous and not synthesis["consensus"]:
        final_rec = "discuss_further"
    
    return {
        "recommendation": final_rec,
        "confidence": synthesis["confidence"],
        "unanimous": synthesis["consensus"],
        "voices": [
            {
                "role": v["role"],
                "recommendation": v["recommendation"],
                "confidence": v["confidence"],
                "reasoning": v["reasoning"]
            }
            for v in synthesis["voices"]
        ],
        "context": req.decision
    }

@router.get("/voices")
async def council_voices() -> Dict:
    """List available council voices and their roles."""
    return {
        "voices": [
            {
                "role": "architect",
                "description": "Reasons about structure, long-term impact, and system architecture",
                "weight": 0.30,
                "concerns": ["scalability", "maintainability", "technical debt"]
            },
            {
                "role": "skeptic",
                "description": "Identifies risks, failure modes, and hidden assumptions",
                "weight": 0.25,
                "concerns": ["security", "edge cases", "failure modes", "assumptions"]
            },
            {
                "role": "pragmatist",
                "description": "Focuses on shipping, constraints, and practical execution",
                "weight": 0.30,
                "concerns": ["time", "resources", "existing tools", "quick wins"]
            },
            {
                "role": "creative",
                "description": "Explores alternatives, opportunities, and novel approaches",
                "weight": 0.15,
                "concerns": ["innovation", "combinations", "wildcard options", "parallel paths"]
            }
        ],
        "voting": "weighted",
        "consensus_rule": "majority_with_skeptic_veto"
    }
