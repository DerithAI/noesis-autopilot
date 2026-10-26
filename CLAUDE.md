# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Read MISSION.md first** (current state, do-not-touch list, open decisions); CHECKPOINT_*.md
files are newer status snapshots. AGENTS.md / RUNBOOK.md cover structure and ops.
README's "Project Structure" is fiction: there is no `noesis/` package (only `noesis/autopilot.py`, unused).
AGENTS.md's frontend file names (`src_pages_*.tsx`) are stale too, see below.

## Three systems in one repo

1. **NOESIS KERNEL** (stdlib only, sealed per GENESIS.md). Flat organ modules at the repo root
   (`perception.py`, `truth_stack.py`, `memory_tree.py`, `identity_core.py`, `tribunal.py`,
   `crown.py`, `counterfactual.py`, `homeostasis.py`, `flood.py`, `evolution.py`, `coherence.py`)
   are wired into one cycle by `noesis_kernel.py`: perceive → truth → memory → homeostasis →
   [counterfactual → tribunal(divine_law) → crown → homeostasis gate] → evolution → flood seed/rescue.
   Each organ's `__main__` is its self-test, and the driver checks for an expected marker string
   in that output. If you change an organ's demo output, update `ORGANS` in
   `.claude/skills/run-noesis/driver.py`.
2. **Cognitive autopilot** `noesis_autopilot.py` (stdlib + sqlite3): an OBSERVE→…→EXECUTE loop that
   writes `autopilot_memory.db`. `noesis_insights.py` reads that DB.
3. **EVO-FORGE**: `venture-swarm.py` (5-agent generator; needs Ollama at 127.0.0.1:11434 and
   `~/.claude/skills/skill-forge/forge.py`) outputs to `ventures/<name>/` plus
   `archive/ventures/venture_*.json` records (tracked on purpose, kept off the repo root).
   `forge-bot/` holds the Ollama bot, bridges and MCP memory server.
   `ventures/evo-hub/` is the dashboard: FastAPI `backend/main.py`, which mounts `*_routes.py` routers
   and the `*_bridge.py` clients for M-AI-SELF :8002 and OMEGA :8001 (both degrade gracefully when
   offline). `agents/` holds `evo_agent.py` (Council) and `itdd_agent.py`. `frontend/` is a Vite +
   React + TS app (`src/pages`, `src/components`, `src/lib/api.ts`).

`jarvis/` is a separate, newer assistant (`python jarvis/main.py --cycle`) with its own requirements.txt.

## Commands

On the owner's Windows machine, use `F:\Python311\python.exe` for pytest. Plain `python` there
is a hermes venv without pytest. The kernel and autopilot need only the stdlib, so any python works.

```bash
python .claude/skills/run-noesis/driver.py        # kernel smoke, expect "12/12 organs beat"
python <organ>.py                                  # one organ's self-test
python noesis_autopilot.py --cycles 5
python -m pytest tests/test_coherence_flood.py     # kernel unit tests (coherence + flood)
python -m pytest tests/test_coherence_flood.py::test_name   # single test
cd forge-bot && python -m pytest test_bot.py -q    # 23 tests
cd ventures/evo-hub && python -m pytest tests/ -q  # test_itdd.py + test_e2e_actions.py (TestClient, all subprocesses mocked)
cd ventures/<venture> && python -m pytest tests/   # per-venture scaffold tests
cd ventures/evo-hub/frontend && npm install && npm run build   # also: npm test (vitest), npm run typecheck, npm run dev
cd ventures/evo-hub/backend && python -m uvicorn main:app --port 8000
```

`tests/test_system.py` needs a populated `nexus_memory.db`, which is gitignored and local-only, so it
fails in fresh clones. The root `requirements.txt` is auto-generated and doesn't cover forge-bot or
EVO-HUB (see `ventures/evo-hub/backend/requirements.txt`).

## Gotchas

- `divine_law.py` is immutable by covenant (GENESIS.md). Never edit it.
- `autopilot_memory.db` and `nexus_memory.db` are gitignored but required at runtime. Don't delete them.
- Port 8000 is occupied by LUMEN on the owner's machine (unresolved conflict with the EVO-HUB backend).
- The repo-local skill `.claude/skills/run-noesis` is shadowed by a global skill pointing at
  `C:\HERMES_`. Invoke the driver by its explicit path.
- `.claude/` is gitignored, and repo-local skill files were force-added.
- forge-bot bridge tests depend on Windows junctions (WOLF_AI, IMPULSE path hardcoded in
  `forge-bot/impulse_bridge.py`).
- Docs mix Polish and English. Match the language of the file you're editing.
