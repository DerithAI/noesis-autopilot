# EVO-HUB Runbook / Cookbook

> Operational guide for running, developing, and troubleshooting the EVO-HUB ecosystem.
> Last updated: 2026-07-04

---

## Quick Start (5 minutes)

### 1. Start Dependencies
```bash
# Terminal 1: Ollama (must have models pulled)
ollama serve

# Terminal 2: M-AI-SELF (port 8002)
cd C:\Users\Main\SELF-EVOLVING-SYSTEM\m-ai-self
python -m uvicorn apps.api.main:app --port 8002
```

### 2. Start EVO-HUB Backend
```bash
cd ventures/evo-hub/backend
python -m uvicorn main:app --port 8000
```

### 3. Start EVO-HUB Frontend
```bash
cd ventures/evo-hub/frontend
npm install   # first time only
npm start     # port 3000
```

### 4. Verify Everything
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/status
curl http://127.0.0.1:8000/api/ventures
curl http://127.0.0.1:8002/health
```

Open browser: `http://localhost:3000/dashboard`

---

## Architecture Overview

```
Frontend (React)          Backend (FastAPI)              External
     :3000                      :8000                     
       │                          │                        
Dashboard ─────────────────────> │ ───> Ollama (11434)     
Council    ─────────────────────> │ ───> M-AI-SELF (8002)   
                                  │ ───> WOLF_AI (junction) 
                                  │ ───> OMEGA (8001) *     
                                  │                        
* = optional, bridge ready        │                        
```

---

## Ports Reference

| Service | Port | Required? |
|---------|------|-----------|
| EVO-HUB Frontend | 3000 | Yes |
| EVO-HUB API | 8000 | Yes |
| M-AI-SELF API | 8002 | Yes (for memory + binding) |
| Ollama | 11434 | Yes (for LLM generation) |
| OMEGA Gateway | 8001 | No (bridge ready, activates when started) |
| LUMEN OS | 8002 | Same as M-AI-SELF |

---

## Daily Development Commands

### Run Tests (All Systems)
```bash
# forge-bot (19 tests, ~3s)
cd forge-bot && python -m pytest test_bot.py -q

# EVO-HUB ITDD (8 tests)
cd ventures/evo-hub && python -m pytest tests/test_itdd.py -q

# noesis core (requires nexus_memory.db)
cd tests && python -m pytest test_system.py -q

# EVO-HUB backend (API tests via TestClient)
cd ventures/evo-hub/backend && python -c "from main import app; from fastapi.testclient import TestClient; c=TestClient(app); print('Health:', c.get('/health').status_code)"
```

### Generate a Venture
```bash
# Via CLI
python venture-swarm.py "your idea" --model qwen2.5:7b --deploy

# Via Dashboard
# Open http://localhost:3000/dashboard
# Click "+ Generate Venture", enter seed, select model, click Generate
```

### Check All Bridges
```bash
# M-AI-SELF
curl http://127.0.0.1:8000/api/mas/health

# Hybrid Memory
curl http://127.0.0.1:8000/api/memory2/status

# Project Binding
curl http://127.0.0.1:8000/api/mas/projects/list

# OMEGA (shows offline if not running)
curl http://127.0.0.1:8000/api/omega/health

# WOLF
cd forge-bot && python bot.py status
```

### Cognitive Council (SUPERPOWERS L3)
```bash
# Via API
curl -X POST http://127.0.0.1:8000/api/council/deliberate \
  -H "Content-Type: application/json" \
  -d '{"decision": "Should we deploy to production?", "context": "Current stage is implement"}'

# Via Dashboard
# Open http://localhost:3000/council
```

### Run EVO Agent with Council
```bash
cd ventures/evo-hub
python agents/evo_agent.py loop "your prompt"
python agents/evo_agent.py council "decision to make"
python agents/evo_agent.py status
```

---

## Docker Compose (Optional)

```bash
cd ventures/evo-hub
docker-compose up --build
```

This starts:
- `evo-hub-api` on port 8000
- `evo-hub-ui` (nginx) on port 3000

External services (Ollama, M-AI-SELF) must run separately or via `host.docker.internal`.

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `REACT_APP_API_URL` | `http://127.0.0.1:8000` | Frontend API base URL |
| `OLLAMA_HOST` | `127.0.0.1:11434` | Ollama server address |
| `CORS_ORIGINS` | `localhost:3000,5173` | Allowed CORS origins |
| `LUMEN_HOST` | `http://host.docker.internal:8002` | M-AI-SELF in Docker |
| `TELEGRAM_BOT_TOKEN` | — | Telegram bot (optional) |

---

## Troubleshooting

### "Ollama connection refused"
```bash
# Check if Ollama is running
curl http://127.0.0.1:11434/api/tags
# If fails: ollama serve
# If using Docker Desktop: host.docker.internal instead of 127.0.0.1
```

### "M-AI-SELF not available"
```bash
# Check port 8002
curl http://127.0.0.1:8002/health
# If fails: cd C:\Users\Main\SELF-EVOLVING-SYSTEM\m-ai-self && uvicorn apps.api.main:app --port 8002
# EVO-HUB will fallback to local SQLite, but semantic search won't work
```

### "CORS error in browser"
- Check `CORS_ORIGINS` env var includes your frontend URL
- Default allows `localhost:3000` and `localhost:5173`

### "Rate limited (429)"
- Action endpoints have 10s cooldown per IP
- Wait or restart backend (in-memory limiter resets)

### "Venture-Swarm timeout"
- Default timeout is 5 minutes
- Use smaller model (`qwen2.5:3b`) for faster generation
- Check Ollama GPU availability

### "Tests fail"
```bash
# forge-bot tests need requests
cd forge-bot && pip install requests pytest

# noesis tests need nexus_memory.db
cd tests && python -c "import sqlite3; c=sqlite3.connect('nexus_memory.db'); c.execute('CREATE TABLE IF NOT EXISTS episodes (id TEXT, content TEXT)'); c.commit()"

# EVO-HUB ITDD needs noesis-autopilot in path
cd ventures/evo-hub && pip install -e ../../
```

---

## File Map

### Entry Points
| File | What It Does |
|------|-------------|
| `noesis_autopilot.py` | Standalone cognitive loop (stdlib only) |
| `venture-swarm.py` | 5-agent pipeline to generate ventures |
| `forge-bot/bot.py` | AI bot with Ollama brain + tools |
| `ventures/evo-hub/backend/main.py` | EVO-HUB FastAPI backend |
| `ventures/evo-hub/frontend/src/App.tsx` | EVO-HUB React frontend |

### Key Backend Modules
| File | Purpose |
|------|---------|
| `dash_routes.py` | Dashboard data (ventures, status, pipeline) |
| `action_routes.py` | Real action backends (generate, test, cognitive, howl) |
| `itdd_routes.py` | ITDD compliance scoreboard |
| `council_routes.py` | SUPERPOWERS L3 Cognitive Council API |
| `m_ai_self_bridge.py` | HTTP client for M-AI-SELF (port 8002) |
| `mas_routes.py` | Proxy endpoints for M-AI-SELF |
| `memory_adapter.py` | Hybrid memory (MAS semantic + SQLite fallback) |
| `memory2_routes.py` | Memory API v2 |
| `omega_routes.py` | OMEGA gateway probe |

### Key Frontend Modules
| File | Purpose |
|------|---------|
| `Dashboard.tsx` | Master dashboard with ventures, status, ITDD, actions |
| `Council.tsx` | 4-voice deliberation UI |
| `Sidebar.tsx` | Navigation with Dashboard, Council, Charts, Tables |

### Agents
| File | Purpose |
|------|---------|
| `agents/evo_agent.py` | 6-stage cognitive loop + Council Pattern |
| `agents/itdd_agent.py` | ITDD compliance checker |

---

## Skills

| Skill | Location | Purpose |
|-------|----------|---------|
| `evo-dash` | `~/.claude/skills/evo-dash/SKILL.md` | Generate dashboard |
| `superpowers` | `~/.claude/skills/superpowers/SKILL.md` | Cognitive patterns L3-L5 |
| `skill-forge` | `~/.claude/skills/skill-forge/forge.py` | Generate skills from intent |

---

## Self-Critique Results

Last audit: 2026-07-04
- CORS: FIXED (whitelist instead of *)
- Rate limiting: FIXED (10s per IP)
- TypeScript `any`: FIXED (proper types)
- ARIA: FIXED (17 attributes)
- prefers-reduced-motion: FIXED
- useMemo/useCallback: FIXED
- Docker HEALTHCHECK: FIXED
- Confidence: 0% → 85%+ (8 issues resolved)

---

## Next Moves

1. **Run tests**: `cd forge-bot && pytest -q && cd ../ventures/evo-hub && pytest tests/ -q`
2. **Start all services**: Ollama → M-AI-SELF → EVO-HUB backend → EVO-HUB frontend
3. **Open dashboard**: `http://localhost:3000/dashboard`
4. **Try Council**: `http://localhost:3000/council` → "Should we add X?"
5. **Generate venture**: Dashboard → + Generate Venture

---

*Built with: EVO-FORGE v4.0 + M-AI-SELF + OMEGA Bridge + SUPERPOWERS L3-L4*
