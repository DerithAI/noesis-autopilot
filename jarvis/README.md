# JARVIS — Persistent AI Assistant

One Cycle. Six Steps. Zero Dependencies (core).

```
SEED (who I am)
 │
 ▼
┌─────────────┐
│    SEE      │ ← perception
└──────┬──────┘
       │
┌──────▼──────┐
│   THINK     │ ← cognition
└──────┬──────┘
       │
┌──────▼──────┐
│    DO       │ ← action
└──────┬──────┘
       │
┌──────▼──────┐
│   CHECK     │ ← evaluation
└──────┬──────┘
       │
┌──────▼──────┐
│  REMEMBER   │ ← memory
└──────┬──────┘
       │
┌──────▼──────┐
│   ADAPT     │ ← evolution
└──────┬──────┘
       │
       ▼
    SEED (enriched)
```

## Quick Start

```bash
cd jarvis
python main.py              # Interactive mode
python main.py --cycle      # Run one cycle
python main.py --input "turn on lights"
python main.py --stats      # Memory stats
```

## Architecture

```
jarvis/
├── core/
│   ├── cycle.py    # MONAD cycle (SEE→THINK→DO→CHECK→REMEMBER→ADAPT)
│   └── seed.py     # Identity, rights, goals, state
├── voice/
│   └── __init__.py # TTS/STT interface
├── scheduler/
│   └── __init__.py # Proactive task scheduling
├── memory/
│   └── __init__.py # SQLite capsule storage
├── home/           # (Coming soon) Smart home integration
├── dashboard/      # (Coming soon) Web UI
├── main.py         # Entry point
└── requirements.txt
```

## Features

- ✅ **MONAD Cycle** — Persistent cognitive loop
- ✅ **Experience Capsules** — Every cycle saves memory
- ✅ **CALM Metric** — Coherence And Life Metric (0.0-1.0)
- ✅ **SQLite Memory** — Persistent, queryable storage
- ✅ **Proactive Scheduler** — Background tasks on timer
- ✅ **Voice Interface** — TTS/STT (system/whisper)
- 🔄 **Home Integration** — MQTT, REST APIs (coming soon)
- 🔄 **Dashboard** — Web UI (coming soon)

## License

MIT
