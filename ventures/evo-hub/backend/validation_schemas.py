"""
Pydantic Validation Schemas for EVO-HUB API
Phase 2.4: Input validation for all endpoints
"""
from pydantic import BaseModel, Field, EmailStr, HttpUrl, field_validator, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pathlib import Path
import re

# ── Enums ──

class VentureStatus(str, Enum):
    DEPLOYED = "deployed"
    LIVE = "live"
    FAILED = "failed"
    GENERATING = "generating"

class PipelineStage(str, Enum):
    OBSERVE = "Observe"
    RESEARCH = "Research"
    ARCHITECT = "Architect"
    IMPLEMENT = "Implement"
    TEST = "Test"
    DEPLOY = "Deploy"

class CognitiveMode(str, Enum):
    CHAT = "chat"
    ANALYZE = "analyze"
    GENERATE = "generate"
    VERIFY = "verify"

class HowlFrequency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    AUUUU = "AUUUU"

class ModelComplexity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# ── Base Models ──

class BaseRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

# ── Venture Schemas ──

class VentureSeed(BaseModel):
    seed: str = Field(..., min_length=3, max_length=200, description="Venture seed idea")
    model: Optional[str] = Field(None, pattern=r"^(qwen2\.5:3b|qwen2\.5:7b|deepseek-r1|qwen3:8b|llama3\.2:3b|hermes3:7b|dolphin3:7b)$")
    stack: str = Field(default="auto", pattern=r"^(auto|fastapi|fastapi\+react|nextjs|django|express)$")
    complexity: ModelComplexity = Field(default=ModelComplexity.MEDIUM)

    @field_validator("seed")
    @classmethod
    def validate_seed(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Seed cannot be empty")
        # Remove potentially dangerous characters
        if re.search(r'[;&|`$]', v):
            raise ValueError("Seed contains invalid characters")
        return v.strip()

class VentureResponse(BaseModel):
    name: str
    seed: str
    stack: str
    files: int = Field(ge=0)
    status: VentureStatus
    created_at: Optional[datetime] = None

# ── System Status Schemas ──

class SystemStatusResponse(BaseModel):
    evo_hub: bool
    lumen: bool
    ollama: bool
    ventures: int = Field(ge=0)

class PipelineResponse(BaseModel):
    steps: List[str]
    current: str
    active_venture: str

# ── Action Schemas ──

class GenerateRequest(BaseModel):
    seed: str = Field(..., min_length=3, max_length=200)
    model: str = Field(default="qwen2.5:7b", pattern=r"^(qwen2\.5:3b|qwen2\.5:7b|deepseek-r1|qwen3:8b|llama3\.2:3b|hermes3:7b|dolphin3:7b)$")
    stack: str = Field(default="auto", pattern=r"^(auto|fastapi|fastapi\+react|nextjs|django|express)$")

class CognitiveRequest(BaseModel):
    input: str = Field(..., min_length=1, max_length=5000)
    mode: CognitiveMode = Field(default=CognitiveMode.CHAT)

class HowlRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    frequency: HowlFrequency = Field(default=HowlFrequency.MEDIUM)

class CognitiveLoopRequest(BaseModel):
    input: str = Field(..., min_length=1, max_length=5000)
    use_council: bool = Field(default=True)

# ── ITDD Schemas ──

class ITDDEntry(BaseModel):
    venture: str
    compliant: bool
    tests: int = Field(ge=0)
    passed: int = Field(ge=0)
    failed: int = Field(ge=0)
    note: Optional[str] = None

class ITDDStatusResponse(BaseModel):
    total_ventures: int = Field(ge=0)
    compliant: int = Field(ge=0)
    with_tests: int = Field(ge=0)
    coverage_ratio: float = Field(ge=0.0, le=1.0)
    compliance_ratio: float = Field(ge=0.0, le=1.0)
    scoreboard: List[ITDDEntry]

# ── Council Schemas ──

class CouncilVoiceResponse(BaseModel):
    role: str
    recommendation: str
    confidence: int = Field(ge=0, le=100)
    reasoning: str

class CouncilDeliberateRequest(BaseModel):
    decision: str = Field(..., min_length=3, max_length=1000)
    context: str = Field(default="", max_length=2000)
    require_unanimous: bool = Field(default=False)

class CouncilDeliberateResponse(BaseModel):
    recommendation: str
    confidence: int = Field(ge=0, le=100)
    unanimous: bool
    voices: List[CouncilVoiceResponse]
    context: str

class CouncilVoicesResponse(BaseModel):
    voices: List[Dict[str, Any]]

# ── Memory Schemas ──

class MemorySearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=5, ge=1, le=50)

class MemorySearchResult(BaseModel):
    source: str
    id: Optional[str] = None
    content: str
    timestamp: Optional[str] = None
    score: Optional[float] = None

class MemorySearchResponse(BaseModel):
    query: str
    count: int = Field(ge=0)
    sources: List[str]
    results: List[MemorySearchResult]

class EpisodicMemoryEntry(BaseModel):
    id: str
    file: str
    task: Dict[str, Any]
    artifact: Dict[str, Any]

class EpisodicMemoryResponse(BaseModel):
    count: int = Field(ge=0)
    memories: List[EpisodicMemoryEntry]

class CheckpointEntry(BaseModel):
    id: str
    file: str
    checkpoint_id: str
    timestamp: str
    data: Dict[str, Any]

class CheckpointsResponse(BaseModel):
    count: int = Field(ge=0)
    checkpoints: List[CheckpointEntry]

class ConversationEntry(BaseModel):
    role: str
    content: str
    timestamp: str

class ConversationResponse(BaseModel):
    count: int = Field(ge=0)
    history: List[ConversationEntry]

# ── OMEGA Schemas ──

class OmegaHealthResponse(BaseModel):
    available: bool
    gateway: str
    status: str
    note: Optional[str] = None

class OmegaNode(BaseModel):
    name: str
    port: int
    capabilities: List[str]

class OmegaNodesResponse(BaseModel):
    available: bool
    nodes: List[OmegaNode] = []
    error: Optional[str] = None

class DispatchPayload(BaseModel):
    target_node: str = Field(..., min_length=1)
    task_data: Dict[str, Any]

class DispatchResponse(BaseModel):
    success: bool
    error: Optional[str] = None

# ── Error Response ──

class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
    field: Optional[str] = None

# ── Validation Utilities ──

class ValidationError(BaseModel):
    field: str
    message: str
    type: str

def validate_request(model_class: type, data: dict) -> tuple[bool, list]:
    """Validate data against a Pydantic model, return (success, errors)."""
    try:
        model_class(**data)
        return True, []
    except Exception as e:
        errors = []
        if hasattr(e, 'errors'):
            for err in e.errors():
                errors.append({
                    "field": ".".join(str(x) for x in err.get("loc", [])),
                    "message": err.get("msg", "Validation error"),
                    "type": err.get("type", "validation_error")
                })
        else:
            errors.append({"field": "body", "message": str(e), "type": "validation_error"})
        return False, errors

# Export all models
__all__ = [
    # Enums
    "VentureStatus", "PipelineStage", "CognitiveMode", "HowlFrequency", "ModelComplexity",
    # Venture
    "VentureSeed", "VentureResponse",
    # System
    "SystemStatusResponse", "PipelineResponse",
    # Actions
    "GenerateRequest", "CognitiveRequest", "HowlRequest", "CognitiveLoopRequest",
    # ITDD
    "ITDDEntry", "ITDDStatusResponse",
    # Council
    "CouncilVoiceResponse", "CouncilDeliberateRequest", "CouncilDeliberateResponse", "CouncilVoicesResponse",
    # Memory
    "MemorySearchRequest", "MemorySearchResult", "MemorySearchResponse",
    "EpisodicMemoryEntry", "EpisodicMemoryResponse",
    "CheckpointEntry", "CheckpointsResponse",
    "ConversationEntry", "ConversationResponse",
    # OMEGA
    "OmegaHealthResponse", "OmegaNode", "OmegaNodesResponse",
    "DispatchPayload", "DispatchResponse",
    # Errors
    "ErrorResponse", "ValidationError",
    # Utils
    "validate_request",
]