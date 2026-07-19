# MISSION — noesis-autopilot

> Agent-facing briefing. Read this before README.md — the README's package layout is fiction (see Architektura). AGENTS.md is the source of truth for structure; this file is the source of truth for current state.

## Co to jest

Three systems in one repo:

1. **Cognitive autopilot** — `noesis_autopilot.py` (stdlib + sqlite3, zero deps). OBSERVE→REMEMBER→DELIBERATE→DECIDE→EXECUTE loop with Council of 6, energy budget, coherence tracking.
2. **NOESIS KERNEL** — the 13-organ engine, sealed 2026-07-08 (GENESIS.md). Flat organ files at repo root (`divine_law.py`, `perception.py`, `truth_stack.py`, `memory_tree.py`, `identity_core.py`, `tribunal.py`, `crown.py`, `counterfactual.py`, `homeostasis.py`, `flood.py`, `evolution.py`) wired by `noesis_kernel.py`. Each organ's `__main__` is a self-test.
3. **EVO-FORGE ecosystem** — `venture-swarm.py` (5-agent venture generator), `forge-bot/` (Ollama bot + bridges, tested), `ventures/evo-hub/` (FastAPI backend :8000 + React frontend :3000, master dashboard).

## Aktualny stan (2026-07-18)

- Kernel: **12/12 organ self-tests pass** (`driver.py`, verified today).
- forge-bot: **23/23 tests pass** (verified today, ~1s).
- EVO-HUB ITDD: **7 passed, 1 skipped** (verified today).
- **EVO-HUB v1.1 (Production Hardening): 8/10 done, delivered 2026-07-18** (see ROADMAP Phase 2 for per-task commits).
  - Remaining: 2.5 fetch retry logic, 2.7 E2E test (generate→test→deploy).
  - ITDD scoreboard: 7/7 ventures with tests, compliance 1.0 (scaffold-level tests — ventures have no app code).

## Architektura (skrót)

**README's "Project Structure" section is aspirational — the `noesis/` package with `core.py`, `db/`, `memory/`, `vector/`, `lattice/`, `tools/` DOES NOT EXIST.** The `noesis/` dir contains only `autopilot.py` (mostly-empty package, don't use) and `test_system.py`. Real entry points:

| What | File |
|------|------|
| Autopilot loop | `noesis_autopilot.py` (388 lines, standalone) |
| Kernel (13 organs) | `noesis_kernel.py` + flat organ files at root |
| Insights report | `noesis_insights.py` → reads `autopilot_memory.db` |
| Venture generator | `venture-swarm.py` (needs Ollama + `~/.claude/skills/skill-forge/forge.py`) |
| Bot | `forge-bot/bot.py` |
| Dashboard backend | `ventures/evo-hub/backend/main.py` (FastAPI, 19+ endpoints) |
| Dashboard frontend | `ventures/evo-hub/frontend/src/App.tsx` |

Full structure, deps, quirks: **AGENTS.md**. Ops (startup, ports, troubleshooting): **RUNBOOK.md**.

## Jak zacząć

```bash
# Kernel smoke test (12/12 expected)
python .claude/skills/run-noesis/driver.py

# Autopilot sanity check
python noesis_autopilot.py --cycles 5

# EVO-HUB backend — WARNING: port 8000 is currently occupied by LUMEN
# MEGA-PLATFORM (conflict unresolved; pick another port or stop LUMEN first)
cd ventures/evo-hub/backend && F:\Python311\python.exe -m uvicorn main:app --port 8000

# Tests — use F:\Python311\python.exe explicitly; plain `python` in PATH
# may resolve to a hermes venv WITHOUT pytest
cd forge-bot && F:\Python311\python.exe -m pytest test_bot.py -q          # 23 passed
cd ventures/evo-hub && F:\Python311\python.exe -m pytest tests/test_itdd.py -q  # 7 passed, 1 skipped
```

## Czego NIE ruszać

- **`divine_law.py`** — immutable by covenant (GENESIS.md: "supreme & immutable; the system cannot edit it").
- **`autopilot_memory.db`**, **`nexus_memory.db`** — gitignored but required at runtime; tests fail without `nexus_memory.db`. Delete only if deliberately resetting state.
- **WOLF_AI / IMPULSE junctions** — `C:\Users\Main\WOLF_AI` → `_VAULT_EXTRACT\WOLF_AI`; IMPULSE path hardcoded in `impulse_bridge.py`. Breaking them breaks forge-bot bridges.
- **Tracked `venture_*.json`** records at repo root — deploy artifacts kept in git on purpose.

## Aktualny focus

v1.2 (ROADMAP Phase 3) — but first the structural blocker: the frontend is a flat
scaffold (no `package.json`/`tsconfig.json`, flat `src_*` filenames) and cannot build.
Restructure it before any polish tasks. Leftovers from v1.1: 2.5 fetch retry, 2.7 E2E.
Open decision: port 8000 conflict with LUMEN (stop LUMEN vs move EVO-HUB).

## Znane problemy

- **Port 8000 conflict** — LUMEN MEGA-PLATFORM listens on 8000; EVO-HUB backend wants the same port. Unresolved.
- **Global skill shadowing** — a global `~/.claude/skills/run-noesis/` exists and points at `C:\HERMES_`, shadowing this repo's `.claude/skills/run-noesis/`. Use the repo-local driver by explicit path.
- **README structure is fiction** — see Architektura above.
- **loguru** added to `ventures/evo-hub/backend/requirements.txt` 2026-07-18 — reinstall backend deps if imports fail.
- `.claude/` is gitignored here; the repo-local skill was force-added.

## Historia decyzji

- **Stability-based coherence** — coherence rewards a settled state, not file growth; rewarding growth killed 60+ prior incarnations (README "Coherence Formula" explains the math).
- **13-organ seal** — GENESIS.md, 2026-07-08. Myth is the interface; tested code underneath. No empty altars.
- **Coherence before expansion** — the covenant. Expansion (EVOLUTION, organ XIII) is last, gated by every organ above it. Applies to the builder too: small verified increments, commit per step.
