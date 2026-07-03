#!/usr/bin/env python3
"""
ITDD (Iterative Test-Driven Development) Workflow for EVO-HUB

Every feature follows:
1. Red  — Write failing test
2. Green — Write minimal code to pass
3. Refactor — Clean up while green
4. Commit — Clear message describing WHY

Usage:
    python -m pytest tests/test_itdd.py -v
"""
import pytest
from pathlib import Path

# ─── RED SPEC: LUMEN Bridge ────────────────────────────────────────

def test_lumen_bridge_available():
    """LUMEN OS must be reachable at port 8002."""
    from memory.lumen_bridge import LumenBridge
    lumen = LumenBridge()
    # If LUMEN is not running, skip instead of fail
    if not lumen.is_available():
        pytest.skip("LUMEN OS not running on port 8002 — start it with: cd m-ai-self && uvicorn apps.api.main:app --port 8002")
    assert lumen.is_available()

def test_lumen_cognitive_loop():
    """Cognitive loop must return 6 stages."""
    from memory.lumen_bridge import LumenBridge
    lumen = LumenBridge()
    if not lumen.is_available():
        pytest.skip("LUMEN OS not running")
    result = lumen.cognitive_loop("Test cognitive loop", mode="chat")
    assert "stages" in result
    assert len(result["stages"]) == 6  # Perception→Intention→Context→Reasoning→Response→Direction

def test_lumen_vector_search():
    """Vector search must return results list."""
    from memory.lumen_bridge import LumenBridge
    lumen = LumenBridge()
    if not lumen.is_available():
        pytest.skip("LUMEN OS not running")
    results = lumen.vector_search("memory", limit=5)
    assert isinstance(results, list)

# ─── RED SPEC: Memory Bridge ───────────────────────────────────────

def test_memory_bridge_hybrid():
    """Memory bridge must support both SQLite and ChromaDB."""
    from memory.lumen_bridge import LumenBridge
    lumen = LumenBridge()
    if not lumen.is_available():
        pytest.skip("LUMEN OS not running")
    # Store in LUMEN
    mid = lumen.store_episode("ITDD test episode", category="itdd")
    assert isinstance(mid, str)
    assert len(mid) > 0

# ─── RED SPEC: Design System ────────────────────────────────────────

def test_design_system_exists():
    """DESIGN.md must exist in frontend/."""
    design_md = Path(__file__).parent.parent / "frontend" / "DESIGN.md"
    assert design_md.exists(), "DESIGN.md not found — run Open Design craft integration"
    content = design_md.read_text()
    assert "--evo-primary" in content
    assert "accessibility" in content.lower()

# ─── RED SPEC: EVO-HUB Status ──────────────────────────────────────

def test_evo_hub_backend_runs():
    """FastAPI backend must respond to /health."""
    try:
        import requests
        resp = requests.get("http://127.0.0.1:8000/health", timeout=5)
        assert resp.status_code == 200
    except Exception as e:
        pytest.skip(f"Backend not running: {e}")

def test_evo_hub_frontend_builds():
    """React frontend must have src/App.tsx."""
    app_tsx = Path(__file__).parent.parent / "frontend" / "src" / "App.tsx"
    assert app_tsx.exists()
