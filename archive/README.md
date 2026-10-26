# archive/

Historical output moved off the repository root so the live entrypoints stay visible. Every file here is still tracked. The kernel and the autopilot do not import these files.

| Folder | Contents |
|--------|----------|
| `ventures/` | 246 `venture_*.json` result records from `venture-swarm.py`. Still tracked. New swarm runs append here (`VENTURE_RECORD_DIR` in `venture-swarm.py`). The matching code packages, when they exist, live under `ventures/` at the repo root. |
| `snapshots/` | `brain_snapshot.json`, `noesis_brain_export.json`, `noesis_brain_v3.json`. Frozen memory exports. Live dashboard exports go to gitignored `brain_exports/`. |
| `sessions/` | `session-ses_0dc0.md`, a single chat transcript. |

Kernel organ modules stay at the repository root on purpose. See `GENESIS.md` and the layout table in `README.md`.
