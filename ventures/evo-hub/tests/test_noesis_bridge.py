#!/usr/bin/env python3
"""
NOESIS bridge contract tests (TDD).

RED: EVO-HUB backend has no NOESIS integration — the second brain's
episodic store (autopilot_memory.db, 70k+ episodes) is invisible to
the unified dashboard. Multi-brain rule: one dashboard reads from
BOTH brains, never a single source.

Expected:
- /noesis/status returns count, last cycle, coherence, energy
- bridge degrades gracefully when DB missing
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_noesis_bridge_reads_db(tmp_path):
    """Bridge must read episodes table and return aggregate stats."""
    import sqlite3
    db = tmp_path / "autopilot_memory.db"
    con = sqlite3.connect(str(db))
    con.execute("""CREATE TABLE episodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT, cycle INTEGER, event_type TEXT,
        content TEXT, coherence REAL, energy REAL)""")
    con.executemany(
        "INSERT INTO episodes (timestamp, cycle, event_type, content, coherence, energy) VALUES (?,?,?,?,?,?)",
        [
            ("2026-07-04T01:00:00", 1, "autopilot_cycle", "cycle one", 0.9, 0.8),
            ("2026-07-04T01:01:00", 2, "autopilot_cycle", "cycle two", 0.95, 0.85),
            ("2026-07-04T01:02:00", 3, "goal_complete", "done", 0.99, 0.9),
        ],
    )
    con.commit()
    con.close()

    from memory.noesis_bridge import NoesisBridge
    bridge = NoesisBridge(db_path=str(db))
    status = bridge.status()

    assert status["count"] == 3
    assert status["last_cycle"] == 3
    assert status["avg_coherence"] is not None
    assert status["event_types"] == {"autopilot_cycle": 2, "goal_complete": 1}


def test_noesis_bridge_missing_db():
    """Bridge must not crash when the DB file is absent."""
    from memory.noesis_bridge import NoesisBridge
    bridge = NoesisBridge(db_path="C:/nonexistent/autopilot_memory.db")
    status = bridge.status()
    assert status["count"] == 0
    assert status["error"] is not None
