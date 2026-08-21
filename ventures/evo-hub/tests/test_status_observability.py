#!/usr/bin/env python3
"""
Observability tests: status.py must exist and return the full stack shape.
"""
import json
import subprocess
import sys
from pathlib import Path

EVO_HUB = Path(__file__).parent.parent


def test_status_script_exists():
    """status.py must exist at evo-hub root."""
    assert (EVO_HUB / "status.py").exists()


def test_status_json_shape():
    """status.py --json must return all four services with ok flags."""
    result = subprocess.run(
        [sys.executable, str(EVO_HUB / "status.py"), "--json"],
        capture_output=True, text=True, timeout=60,
        cwd=str(EVO_HUB),
    )
    assert result.returncode == 0, f"status.py failed: {result.stderr[:200]}"
    data = json.loads(result.stdout)
    for svc in ("lumen", "evo_hub", "frontend", "ollama"):
        assert svc in data, f"missing service {svc}"
        assert "ok" in data[svc], f"{svc} missing ok flag"
