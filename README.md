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
git clone <repo>
cd noesis
```

NOESIS uses only Python standard library + SQLite. No pip install needed.

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

### Hermes Integration

```bash
python hermes_bridge.py                 # Start bridge server
# Then in Hermes: @noesis_deliberate("What should I do next?")
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
          + file_growth * 0.2
```

**Thresholds:**
- `< 0.5` → RENEWAL (checkpoint, slow down)
- `≥ 0.5` → EXECUTE (stable, monitor)
- `< 0.3` → FLOOD recovery mode
- `< 10 energy` → QUIESCE (critical stop)

---

## 🔄 Integration Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Standalone** | `noesis_autopilot.py` alone | Any project, any language |
| **Hermes Plugin** | Bridge via `@noesis_deliberate` | AI assistant with memory |
| **Ollama Bridge** | `ollama_bridge.py` | Local LLM + cognition |
| **Python Module** | `from noesis import NoesisKernel` | Custom applications |

---

## 📁 Project Structure

```
noesis/
├── noesis/
│   ├── core.py              # Core kernel
│   ├── bridge.py            # Hermes bridge
│   ├── cli.py               # Command-line interface
│   ├── db/
│   │   ├── database.py      # SQLite engine
│   │   └── repository.py    # Episodic repository
│   ├── memory/
│   │   ├── episodic.py      # Event memory
│   │   ├── semantic.py      # Concept memory
│   │   └── reflection.py    # Self-reflection
│   ├── vector/
│   │   ├── embeddings.py    # Embedding generation
│   │   └── store.py         # ChromaDB store
│   ├── lattice/
│   │   └── graph.py         # NetworkX graph
│   └── tools/
│       ├── filesystem.py    # File operations
│       ├── python_exec.py   # Python execution
│       └── hermes_tools.py  # Hermes interface
├── noesis_autopilot.py      # Standalone autopilot ⭐
├── noesis_insights.py       # Insight engine ⭐
├── hermes_bridge.py         # FastAPI bridge
├── ollama_bridge.py         # Ollama bridge
└── autopilot_memory.db      # Generated: SQLite memory
```

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

## 📜 License

MIT — Build your own mind.

---

*Built with 🔥 by AUUU | NOESIS v1.0 | 2026*
