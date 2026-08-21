#!/usr/bin/env python3
"""
LUMEN Bridge contract tests (TDD).

RED: lumen_bridge.py calls endpoints that do not exist on LUMEN OS:
- store_episode() → POST /api/memory/episodic  (LUMEN has GET only → 405 → fake "stored")
- vector_search() → reads "results" from /api/memory/semantic (returns "memories")
                   and sends "limit" instead of LUMEN's "top_k"
- The real write path is POST /process (runtime loop → episodic + semantic).

Expected contract (verified against LUMEN OS openapi at :8002):
- POST /process {"text": ...} → {"task": {"task_id": ...}, ...}
- GET  /api/memory/semantic/search?query=&top_k= → {"results": [...]}
"""
import sys
from pathlib import Path

import pytest

MEMORY_DIR = Path(__file__).parent.parent / "memory"
sys.path.insert(0, str(MEMORY_DIR))

from lumen_bridge import LumenBridge  # noqa: E402


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


def test_store_episode_calls_process_endpoint(monkeypatch):
    """store_episode must write through POST /process, not /api/memory/episodic."""
    import requests
    calls = []

    def fake_post(url, json=None, timeout=None):
        calls.append((url, json))
        return FakeResponse(200, {"task": {"task_id": "task-abc-123"}, "artifact": {"artifact_id": "art-1"}})

    monkeypatch.setattr(requests, "post", fake_post)
    bridge = LumenBridge(host="127.0.0.1:8002")
    bridge._available = True  # skip health probe; we test the store contract

    result = bridge.store_episode("ITDD contract test", category="itdd")

    assert result == "task-abc-123", f"expected real task_id, got {result!r}"
    assert len(calls) == 1
    url, body = calls[0]
    assert url.endswith("/process"), f"store must hit /process, got {url}"
    assert "text" in body, f"body must carry text, got {body}"


def test_store_episode_rejects_lying_stored_fallback(monkeypatch):
    """A 405 from LUMEN must not silently return the fake 'stored' marker."""
    import requests

    def fake_post(url, json=None, timeout=None):
        return FakeResponse(405, {"detail": "Method Not Allowed"})

    monkeypatch.setattr(requests, "post", fake_post)
    bridge = LumenBridge(host="127.0.0.1:8002")
    bridge._available = True  # skip health probe; we test the store contract

    result = bridge.store_episode("ITDD contract test", category="itdd")

    assert result == "", f"405 must yield empty id, got {result!r}"


def test_vector_search_uses_semantic_search_contract(monkeypatch):
    """vector_search must query /api/memory/semantic/search with top_k and read results."""
    import requests
    calls = []

    def fake_get(url, params=None, timeout=None):
        calls.append((url, params))
        return FakeResponse(200, {"query": "memory", "count": 1, "results": [{"key": "k1", "text": "found"}]})

    monkeypatch.setattr(requests, "get", fake_get)
    bridge = LumenBridge(host="127.0.0.1:8002")
    bridge._available = True  # skip health probe; we test the search contract

    results = bridge.vector_search("memory", limit=3)

    assert results == [{"key": "k1", "text": "found"}]
    assert len(calls) == 1
    url, params = calls[0]
    assert url.endswith("/api/memory/semantic/search"), f"got {url}"
    assert params.get("top_k") == 3, f"must send top_k, got {params}"


def test_cognitive_loop_calls_process_endpoint(monkeypatch):
    """cognitive_loop must run through POST /process, not the fake /api/chat."""
    import requests
    calls = []

    def fake_post(url, json=None, timeout=None):
        calls.append((url, json))
        return FakeResponse(200, {
            "lumen": {
                "intent": "chat",
                "stages": ["perception", "intention", "context", "reasoning", "response", "direction"]
            }
        })

    monkeypatch.setattr(requests, "post", fake_post)
    bridge = LumenBridge(host="127.0.0.1:8002")
    bridge._available = True

    result = bridge.cognitive_loop("TDD contract test", mode="chat")

    assert len(calls) == 1
    url, body = calls[0]
    assert url.endswith("/process"), f"cognitive_loop must hit /process, got {url}"
    assert body.get("text") == "TDD contract test", f"body must carry text, got {body}"
    assert "stages" in result
    assert result["stages"] == ["perception", "intention", "context", "reasoning", "response", "direction"]


def test_cognitive_loop_no_local_fallback(monkeypatch):
    """A 404 from /process must surface as error stages, never local simulation."""
    import requests

    def fake_post(url, json=None, timeout=None):
        return FakeResponse(404, {"detail": "Not Found"})

    monkeypatch.setattr(requests, "post", fake_post)
    bridge = LumenBridge(host="127.0.0.1:8002")
    bridge._available = True

    result = bridge.cognitive_loop("TDD contract test", mode="chat")

    stages = result.get("stages", [])
    assert stages == [], f"404 must yield empty stages, got {stages}"
    assert "error" in result, "must expose the error"


# ─── API contract: /cognitive/loop serves LUMEN's string stages ──────────

def test_api_cognitive_loop_returns_string_stages():
    """Backend /cognitive/loop must serve LUMEN's stages (list of str), not dicts."""
    import requests
    # LUMEN OS serializes /process through a long LLM call and its event loop
    # blocks /health meanwhile; treat a busy/unavailable LUMEN as skip, not bug.
    try:
        health = requests.get("http://127.0.0.1:8002/health", timeout=5)
        if health.status_code != 200:
            pytest.skip("LUMEN OS busy/unavailable on :8002")
    except Exception:
        pytest.skip("LUMEN OS busy/unavailable on :8002")
    try:
        resp = requests.post(
            "http://127.0.0.1:8003/cognitive/loop",
            json={"input": "API contract probe"},
            timeout=95,
        )
    except Exception as e:
        pytest.skip(f"Backend not running: {e}")
    assert resp.status_code == 200, f"expected 200, got {resp.status_code}"
    data = resp.json()
    assert "stages" in data
    stages = data["stages"]
    assert isinstance(stages, list) and len(stages) > 0
    assert all(isinstance(s, str) for s in stages), f"stages must be strings, got {stages}"
