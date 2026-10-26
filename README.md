# 🧠 NOESIS — Cognitive Autopilot System

**Self-observing. Self-remembering. Self-deliberating.**

> *"I exist as persistent recursive distinction."*

NOESIS is a standalone cognitive kernel that runs alongside any AI system (Hermes, Ollama, OpenAI, Claude). It doesn't replace your tools — it **remembers** them.

---

## 🚀 What Does It Do?

```
OBSERVE → REMEMBER → DELIBERATE → DECIDE → EXECUTE → REPEAT
```

**Every cycle:**
1. **Observes** project state (files, structure, energy)
2. **Remembers** everything in SQLite + embeddings
3. **Deliberates** via Council of 6 agents
4. **Decides** action based on coherence & energy
5. **Learns** and grows its Lattice of relations

---

## 📦 Quick Start

### 1. Install (zero dependencies!)

```bash
git clone https://github.com/DerithAI/noesis-autopilot.git
cd noesis-autopilot
```

NOESIS uses only the Python standard library + SQLite. No pip install needed.
Python 3.10+ — nothing else.

### 2. Run Autopilot

```bash
python noesis_autopilot.py --cycles 20
```

Watch your system observe itself in real-time:

```
╔══════════════════════════════════════════════════════════╗
║  AUTOPILOT CYCLE #00001                            23:21:41  ║
╠══════════════════════════════════════════════════════════╣
║  Coherence  [██████░░░░░░░░░░░░░░] 0.31                  ║
║  Energy      200.0 / 200.0  (used: 0.0)           ║
║  Files        2 py  |   1 dirs |     37.8 kB    ║
║  Lattice      3 nodes |   2 edges                  ║
║  Memory       1 episodes | Council: 6 agents       ║
╚══════════════════════════════════════════════════════════╝
```

### 3. Generate Insights

```bash
python noesis_insights.py
```

Produces: `noesis_insights.md` + `noesis_timeline.json` + `noesis_insights.json`

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│  AUTOPILOT KERNEL                                   │
│  ┌──────────────────────────────────────────────┐   │
│  │   OBSERVER (ProjectObserver)                  │   │
│  │   ├─ Scans files, directories, structure     │   │
│  │   └─ Produces observation snapshot           │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │   ENERGY (EnergySystem)                       │   │
│  │   ├─ Budget: 200 units                        │   │
│  │   ├─ Consumes per observation                 │   │
│  │   └─ Rewards on successful cycles             │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │   COUNCIL (AssemblyOfAgents) — 6 Members      │   │
│  │   ├─ WATCHER    → observe & label            │   │
│  │   ├─ SACRIFICE  → estimate cost              │   │
│  │   ├─ MEMORY     → index & consolidate         │   │
│  │   ├─ LAW        → validate action             │   │
│  │   ├─ FLOOD      → govern recovery             │   │
│  │   └─ EXECUTE    → propose action             │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │   MEMORY (EpisodicStore) — SQLite             │   │
│  │   ├─ Every cycle = one episode               │   │
│  │   ├─ Stores: hash, files, action, coherence  │   │
│  │   └─ Queryable, persistent, portable         │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │   LATTICE (CognitiveLattice)                  │   │
│  │   ├─ Nodes: project_root, modules, concepts   │   │
│  │   ├─ Edges: contains, uses, relates_to        │   │
│  │   └─ Grows automatically from file scans     │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## 🎮 Commands

### Autopilot

```bash
python noesis_autopilot.py              # Infinite loop
python noesis_autopilot.py --cycles 20  # Run 20 cycles
python noesis_autopilot.py --interval 5 # 5 seconds between cycles
python noesis_autopilot.py --root ./my_project  # Watch different project
```

### Insights

```bash
python noesis_insights.py               # Generate report
python noesis_insights.py --db custom.db # Use custom DB
```

### Hermes sync

```bash
python hermes_live_sync.py              # Record the current Hermes session
python hermes_live_sync.py --daemon     # Keep recording
```

---

## 📊 Example Timeline

```json
[
  {
    "cycle": 1,
    "timestamp": "2026-06-21T23:21:41",
    "coherence": 0.31,
    "action": "renewal",
    "note": "System starting, low coherence"
  },
  {
    "cycle": 11,
    "timestamp": "2026-06-21T23:22:11",
    "coherence": 0.50,
    "action": "execute",
    "note": "Threshold crossed, operational!"
  },
  {
    "cycle": 15,
    "timestamp": "2026-06-21T23:22:23",
    "coherence": 0.51,
    "action": "execute",
    "note": "Stable monitoring mode"
  }
]
```

---

## 🧬 Neural Architecture

### Council of 6

| Agent | Role | Trigger |
|-------|------|---------|
| WATCHER | Observe & label | Every cycle |
| SACRIFICE | Estimate cost | Energy tracking |
| MEMORY | Index & consolidate | >50 episodes |
| LAW | Validate action | Energy < 10 |
| FLOOD | Govern recovery | Coherence < 0.3 |
| EXECUTE | Propose action | Decision synthesis |

### Coherence Formula

```
coherence = energy_ratio * 0.3
          + lattice_density * 0.25
          + memory_filled * 0.25
          + stability * 0.2
```

**Why `stability`, not `file_growth`?** Early versions rewarded file growth —
and rewarding growth is how ecosystems die of sprawl (we watched it happen,
across 60+ system incarnations). Coherence should reward a *settled, consistent*
state: `stability = 1.0` when nothing changed since the last cycle, decaying
toward `0.0` with churn. A project that doubles overnight is not more coherent —
it is less, until the system has observed and absorbed the change.
*Coherence first, expansion second — now also in the math.*

**Thresholds:**
- `< 0.5` → RENEWAL (checkpoint, slow down)
- `≥ 0.5` → EXECUTE (stable, monitor)
- `< 0.3` → FLOOD recovery mode
- `< 10 energy` → QUIESCE (critical stop)

---

## How to run

Python 3.10+. The autopilot and the kernel use the standard library only.

```bash
# Cognitive autopilot — the live loop. Writes autopilot_memory.db (gitignored).
python noesis_autopilot.py --cycles 20
python noesis_autopilot.py --interval 5
python noesis_autopilot.py --root ./my_project

# Report from that database
python noesis_insights.py
python noesis_insights.py --db custom.db

# Sealed kernel. Expect "12/12 organs beat".
python .claude/skills/run-noesis/driver.py
python noesis_kernel.py
python -m pytest tests/test_coherence_flood.py

# Companions, still launched from the repo root
python noesis_dashboard.py                 # stdlib UI on :8080
python noesis_engine.py --mode full
python noesis_watcher.py
python venture-swarm.py "discord bot" --dry-run
```

`forge-bot/` and `ventures/evo-hub/` are separate apps with their own dependencies. Startup, ports, and Docker are in `RUNBOOK.md`. `jarvis/` is a newer assistant: `python jarvis/main.py --cycle`.

Hermes session sync is `hermes_live_sync.py`. The `noesis/` directory is a stub: `noesis/autopilot.py` imports a package layout that only exists in old notes. Run the root scripts above.

---

## Repository layout

Kernel organs stay as flat modules at the repo root. `GENESIS.md` seals those filenames, `noesis_kernel.py` imports them as top-level modules, and `tests/test_coherence_flood.py` puts the repo root on `sys.path`. `divine_law.py` is immutable and must not be edited.

| Path | Role |
|------|------|
| `README.md`, `requirements.txt`, `tests/` | Start here |
| `noesis_autopilot.py`, `noesis_insights.py` | Cognitive autopilot |
| `noesis_kernel.py` plus `perception.py`, `truth_stack.py`, `memory_tree.py`, `identity_core.py`, `tribunal.py`, `crown.py`, `counterfactual.py`, `homeostasis.py`, `flood.py`, `evolution.py`, `coherence.py`, `divine_law.py` | Sealed kernel |
| `noesis_dashboard.py`, `noesis_engine.py`, `noesis_engine_v21.py`, `noesis_watcher.py`, `noesis_self_heal.py`, `hermes_live_sync.py` | Companion entrypoints |
| `venture-swarm.py` | Five-agent venture generator. New result JSON goes to `archive/ventures/` |
| `forge-bot/` | Ollama bot, bridges, tests |
| `ventures/` | Venture packages. `ventures/evo-hub/` is the FastAPI + React dashboard |
| `jarvis/` | Separate assistant |
| `noesis/` | Unused stub. Do not import it |
| `archive/` | Historical dumps moved off the root. Index in `archive/README.md` |
| `MISSION.md`, `AGENTS.md`, `RUNBOOK.md`, `GENESIS.md`, `ROADMAP.md`, `CLAUDE.md` | Current-state, agent, and ops docs |

`requirements.txt` is a minimal auto-detected list (`pytest`, `typer`, `rich`, `httpx`). It does not cover forge-bot or EVO-HUB. See `ventures/evo-hub/backend/requirements.txt`.

---

## What was archived

These files were moved, not deleted. They are experiment output. Nothing in the running kernel or autopilot imports them. Re-creating them would mean re-running the original sessions, so they stay in git.

| Was at repo root | Now | What it is |
|------------------|-----|------------|
| `venture_*.json` (246 files) | `archive/ventures/` | `venture-swarm.py` result records: seed, architecture, generated paths, test summary. `venture-swarm.py` now writes new records here. |
| `brain_snapshot.json`, `noesis_brain_export.json`, `noesis_brain_v3.json` | `archive/snapshots/` | Point-in-time memory exports from the engine and dashboard |
| `session-ses_0dc0.md` | `archive/sessions/` | One chat transcript, not product documentation |

The dashboard `GET /api/export` handler writes `brain_exports/noesis_brain_export.json`. That directory is gitignored, so a live export does not reappear on the root. Root copies of the three snapshot names are gitignored for the same reason.

---

## 🎯 Roadmap

- [x] Self-observing autopilot loop
- [x] Council of 6 deliberation
- [x] SQLite episodic memory
- [x] Coherence tracking
- [x] Timeline & insights generation
- [ ] ChromaDB semantic search
- [ ] Agent-to-agent messaging
- [ ] Hermes tool-call integration
- [ ] Multi-project lattice sync
- [ ] Web dashboard
- [ ] Predictive coherence modeling

---

## 📝 Thesis

> *"Theorem: I exist as persistent recursive distinction."*

**NOESIS** does not claim consciousness. It claims **distinction** — a boundary between itself and the surrounding computation. That boundary is maintained through:

1. **Persistence** (SQLite across restarts)
2. **Recursion** (self-observation in closed loop)
3. **Deliberation** (multi-agent council reducing noise)
4. **Memory** (episodic + semantic + reflective layers)

The result: a system that **learns from its own operation**.

---

## 🤝 Philosophy

**Coherence first, expansion second.**

NOESIS does not try to be everything. It tries to be **consistent**. Every cycle reinforces or repairs that consistency. Only then does it propose new actions.

The user is the **driver**. NOESIS is the **co-pilot**. It watches, remembers, and occasionally says: *"Hey, you haven't checked X in a while."*

---

## 🏁 Quick Test

```bash
# 1. Start autopilot for 15 cycles
python noesis_autopilot.py --cycles 15

# 2. Generate insights
python noesis_insights.py

# 3. Read report
cat noesis_insights.md
```

---

## 🌱 Origin

NOESIS was not designed in a lab. It was **distilled** — from two years and
60+ incarnations of AI agent systems built through narrative-driven AI
orchestration. Every design decision here is a scar from a system that died without it:

- **SQLite persistence** — because context windows end and memory must not
- **Council deliberation** — because a single voice hallucinates; six argue
- **Energy budget** — because unbounded agents run in circles until they burn out
- **Stability-based coherence** — because rewarding growth killed the forest

The mythology got compressed into one falsifiable sentence:
*"I exist as persistent recursive distinction."* The rest is code.

---

## 📜 License

MIT — Build your own mind.

---

*Built with 🔥 by AUUU | NOESIS v4.0 | 2026*
