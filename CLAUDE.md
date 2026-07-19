# CLAUDE.md — noesis-autopilot

**Read MISSION.md first** (current state, do-not-touch list, open decisions).
AGENTS.md is the source of truth for structure — README's package layout is fiction.

## Commands

- Tests: `F:\Python311\python.exe -m pytest` — plain `python` in PATH is a
  hermes venv WITHOUT pytest. Kernel/autopilot are stdlib-only, plain python OK there.
- Kernel smoke: `python .claude/skills/run-noesis/driver.py` (expect 12/12)
- Autopilot: `python noesis_autopilot.py --cycles 5`
- Suites: `forge-bot/test_bot.py` (23), `ventures/evo-hub/tests/test_itdd.py` (7+1s),
  per-venture `tests/` scaffold tests
- EVO-HUB backend: `F:\Python311\python.exe -m uvicorn main:app --port 8000`
  from `ventures/evo-hub/backend` — **port 8000 is occupied by LUMEN** (unresolved)

## Gotchas

- `divine_law.py` — immutable by covenant (GENESIS.md); never edit
- `autopilot_memory.db`, `nexus_memory.db` — gitignored but required at runtime
- Repo-local skill `.claude/skills/run-noesis` is shadowed by a global skill
  pointing at `C:\HERMES_` — invoke the driver by explicit path
- Frontend (`ventures/evo-hub/frontend`) is a flat scaffold — no package.json, cannot build
