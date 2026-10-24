#!/usr/bin/env python3
"""
NOESIS Bridge for EVO-HUB — reads the second brain's episodic store.

NOESIS autopilot persists episodes to SQLite (autopilot_memory.db):
    id, timestamp, cycle, event_type, content, coherence, energy

Multi-brain rule: the unified dashboard reads from BOTH brains (LUMEN
via lumen_bridge, NOESIS via this bridge), never a single source.
"""
import os
import sqlite3
from typing import Dict, Optional

NOESIS_DB = os.environ.get(
    "NOESIS_DB",
    r"C:\Users\Main\OLLAMA_HERMES\autopilot_memory.db",
)


class NoesisBridge:
    """Read-only bridge to the NOESIS episodic store."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or NOESIS_DB

    def status(self) -> Dict:
        """Return aggregate stats: count, last cycle, coherence, event types."""
        if not os.path.exists(self.db_path):
            return {"count": 0, "error": f"NOESIS DB not found: {self.db_path}"}
        try:
            con = sqlite3.connect(self.db_path)
            con.row_factory = sqlite3.Row
            cur = con.cursor()

            count = cur.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]

            row = cur.execute(
                "SELECT cycle, event_type, coherence, energy, timestamp, content "
                "FROM episodes ORDER BY id DESC LIMIT 1"
            ).fetchone()

            last = None
            if row:
                last = {
                    "cycle": row["cycle"],
                    "event_type": row["event_type"],
                    "coherence": row["coherence"],
                    "energy": row["energy"],
                    "timestamp": row["timestamp"],
                    "content_preview": (row["content"] or "")[:120],
                }

            coherence_row = cur.execute(
                "SELECT AVG(coherence) AS avg_coherence, AVG(energy) AS avg_energy "
                "FROM episodes WHERE coherence IS NOT NULL"
            ).fetchone()

            types = {}
            for r in cur.execute("SELECT event_type, COUNT(*) AS n FROM episodes GROUP BY event_type ORDER BY n DESC LIMIT 10"):
                types[r["event_type"]] = r["n"]

            con.close()
            return {
                "count": count,
                "last_cycle": last["cycle"] if last else None,
                "last": last,
                "avg_coherence": coherence_row["avg_coherence"] if coherence_row else None,
                "avg_energy": coherence_row["avg_energy"] if coherence_row else None,
                "event_types": types,
                "error": None,
            }
        except Exception as e:
            return {"count": 0, "error": str(e)}


if __name__ == "__main__":
    import json
    print(json.dumps(NoesisBridge().status(), indent=2))
