#!/usr/bin/env python3
"""
E2E-style tests for the EVO-HUB Dashboard action flow (ROADMAP v1.1 task 2.7).

Runs the FastAPI app in-process via fastapi.testclient.TestClient — no live
server, no Ollama, no M-AI-SELF required. All heavy subprocess work
(venture-swarm, pytest suites, ITDD scoreboard) is monkeypatched so the suite
is deterministic and fast.

Usage:
    F:\\Python311\\python.exe -m pytest tests/test_e2e_actions.py -q
"""
import os
import sys
import json
import types
import subprocess
from pathlib import Path

import pytest

# ── Import the app the same way the backend runs it ────────────────
BACKEND_DIR = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# Never let the HTTPS-redirect middleware activate inside tests.
os.environ.pop("EVO_HUB_FORCE_HTTPS", None)

from main import app          # noqa: E402
import action_routes          # noqa: E402
import itdd_routes            # noqa: E402  (imported for monkeypatch targets)

# Silence loguru console/file sinks configured by logging_config.
from loguru import logger     # noqa: E402
logger.remove()

from fastapi.testclient import TestClient  # noqa: E402

client = TestClient(app)


# ── Fixtures ───────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _reset_rate_limit():
    """Rate-limit state is module-global; clear it so tests are order-independent."""
    action_routes._rate_limit_store.clear()
    yield
    action_routes._rate_limit_store.clear()


@pytest.fixture
def fake_subprocess_ok(monkeypatch):
    """Replace subprocess.run with an instant fake success. Records calls."""
    calls = []

    def fake_run(cmd, *args, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(
            args=cmd, returncode=0, stdout="5 passed in 0.10s\n", stderr=""
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


@pytest.fixture
def forbid_subprocess(monkeypatch):
    """Any subprocess spawn during the test is a failure."""
    def boom(*args, **kwargs):
        raise AssertionError("subprocess must NOT be spawned in this test")

    monkeypatch.setattr(subprocess, "run", boom)
    monkeypatch.setattr(subprocess, "Popen", boom)


@pytest.fixture
def fake_wolf_bridge(monkeypatch):
    """Inject a fake wolf_bridge module so /api/action/howl never touches
    forge-bot internals (or Ollama, if core.wolf ever materializes)."""
    mod = types.ModuleType("wolf_bridge")

    def wolf_howl(message, frequency="medium"):
        print(json.dumps({"howl": message, "frequency": frequency, "pack": "fake"}))
        return 0

    mod.wolf_howl = wolf_howl
    monkeypatch.setitem(sys.modules, "wolf_bridge", mod)
    return mod


# ── (a) Ventures list ──────────────────────────────────────────────

def test_ventures_list():
    """GET /api/ventures → 200 and at least 7 ventures with sane shape."""
    resp = client.get("/api/ventures")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 7
    for v in data:
        assert "name" in v and "status" in v


# ── (b) ITDD global status ─────────────────────────────────────────

def test_itdd_status_full_coverage(fake_subprocess_ok):
    """GET /api/itdd/status → 200 and with_tests == total_ventures.

    subprocess.run is faked: the real endpoint would spawn pytest per venture
    (including THIS suite — infinite recursion). The fake proves the
    aggregation logic: every venture dir has a tests/ folder, so every one
    gets a pytest invocation and counts as with_tests.
    """
    resp = client.get("/api/itdd/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_ventures"] >= 7
    assert data["with_tests"] == data["total_ventures"]
    assert data["coverage_ratio"] == 1.0
    # one pytest invocation per venture, none of them real
    assert len(fake_subprocess_ok) == data["total_ventures"]


# ── (c) Generate with invalid body → 422, no subprocess ────────────

@pytest.mark.parametrize("body", [
    {},                                  # missing required seed
    {"seed": ""},                        # min_length=1 violated
    {"seed": "x" * 201},                 # max_length=200 violated
    {"seed": "ok", "model": ""},         # model min_length violated
])
def test_generate_invalid_body_422(forbid_subprocess, body):
    """POST /api/action/generate with invalid body → 422 from Pydantic,
    and venture-swarm is never spawned (forbid_subprocess would raise)."""
    resp = client.post("/api/action/generate", json=body)
    assert resp.status_code == 422


# ── (c') Generate with valid body — subprocess faked ───────────────

def test_generate_valid_body_monkeypatched(fake_subprocess_ok):
    """POST /api/action/generate with valid body → 200; venture-swarm is
    monkeypatched to instant success (no Ollama)."""
    resp = client.post("/api/action/generate", json={"seed": "e2e smoke venture"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["seed"] == "e2e smoke venture"
    assert data["returncode"] == 0
    assert len(fake_subprocess_ok) == 1  # exactly one (fake) swarm spawn


# ── (d) Howl with valid body ───────────────────────────────────────

def test_howl_valid_body(fake_wolf_bridge):
    """POST /api/action/howl with valid body → 200 and sane response shape."""
    resp = client.post(
        "/api/action/howl",
        json={"message": "E2E test howl", "frequency": "low"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["sent"] is True
    assert data["message"] == "E2E test howl"
    assert "E2E test howl" in data["raw"]


# ── (e) Rate limiting ──────────────────────────────────────────────

def test_rate_limit_second_call_429(fake_wolf_bridge):
    """Second immediate valid POST to the same action endpoint → 429.

    Verified against action_routes.rate_limit: 1 req / 10 s per IP per
    endpoint, raises HTTPException(429) with a 'Rate limited' detail.
    """
    first = client.post("/api/action/howl", json={"message": "first"})
    assert first.status_code == 200

    second = client.post("/api/action/howl", json={"message": "second"})
    assert second.status_code == 429
    assert "Rate limited" in second.json()["detail"]


def test_rate_limit_is_per_endpoint(fake_wolf_bridge, fake_subprocess_ok):
    """Rate limit keys on IP+endpoint: hitting a different action endpoint
    right after the first one is NOT limited."""
    first = client.post("/api/action/howl", json={"message": "howl then generate"})
    assert first.status_code == 200

    other = client.post("/api/action/generate", json={"seed": "different endpoint"})
    assert other.status_code == 200


# ── (e') Action tests endpoint — subprocess faked ──────────────────

def test_action_tests_monkeypatched(fake_subprocess_ok):
    """GET /api/action/tests → 200 with per-suite results; the real pytest
    subprocesses (which would recursively run THIS suite) are faked."""
    resp = client.get("/api/action/tests")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_suites"] >= 1
    assert data["total_passed"] == data["total_suites"]
    for suite in data["suites"]:
        assert suite["passed"] is True


# ── (f) Full chain smoke ───────────────────────────────────────────

def test_full_chain_smoke():
    """/health → /api/status → /api/pipeline all respond 200.

    Bridge availability (LUMEN, Ollama) is NOT asserted — those degrade
    gracefully and must not affect the smoke result."""
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"

    status = client.get("/api/status")
    assert status.status_code == 200
    sdata = status.json()
    assert sdata["evo_hub"] is True
    assert sdata["ventures"] >= 7

    pipeline = client.get("/api/pipeline")
    assert pipeline.status_code == 200
    pdata = pipeline.json()
    assert isinstance(pdata["steps"], list) and len(pdata["steps"]) == 6
