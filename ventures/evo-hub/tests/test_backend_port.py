#!/usr/bin/env python3
"""
Backend port configuration tests (TDD).

RED: backend/main.py hardcodes port=8000 in uvicorn.run(), ignoring
EVO_HUB_PORT env var. LUMEN MEGA-PLATFORM occupies :8000, so the
EVO-HUB backend can never start on its default port.

Expected behavior:
- get_backend_port() returns EVO_HUB_PORT from environment when set
- get_backend_port() returns 8000 when env var is unset
"""
import os
import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture(autouse=True)
def clean_env():
    """Ensure EVO_HUB_PORT is absent before each test, restore after."""
    original = os.environ.get("EVO_HUB_PORT")
    os.environ.pop("EVO_HUB_PORT", None)
    yield
    if original is None:
        os.environ.pop("EVO_HUB_PORT", None)
    else:
        os.environ["EVO_HUB_PORT"] = original


def test_backend_port_from_env():
    """EVO_HUB_PORT env var must override default port."""
    os.environ["EVO_HUB_PORT"] = "8003"
    from main import get_backend_port

    assert get_backend_port() == 8003


def test_backend_port_defaults_to_8000():
    """Without EVO_HUB_PORT, default port must be 8000."""
    from main import get_backend_port

    assert get_backend_port() == 8000
