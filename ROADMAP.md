# EVO-FORGE Roadmap

> Strategic roadmap for the noesis-autopilot ecosystem.
> Current state: EVO-DASH v1.0 deployed (2026-07-04)
> Next milestone: EVO-DASH v1.1 — Production Hardening

---

## Phase 0: Foundation ✅ COMPLETE

**Delivered:** 2026-07-04

### What Was Built
- **EVO-FORGE v4.0**: Skill generator with Smart Model Router, multi-agent pipeline
- **Venture-Swarm**: 5-agent pipeline (research→architect→implement→test→deploy)
- **Forge-Bot**: AI bot with Ollama brain + 6 tools + 23 tests passing
- **MCP Memory Server**: SQLite + semantic search, dual CLI/MCP mode
- **WOLF Bridge**: Pack integration (status, howl, hunt)
- **7 Ventures**: todo app, discord bot, saas api, crypto scraper, ai assistant, evo learning path, evo-hub

### Verification
```bash
cd forge-bot && python -m pytest test_bot.py -q  # 23 passed
cd ventures/evo-hub && python -m pytest tests/test_itdd.py -q  # 8 passed
python noesis_autopilot.py --cycles 5  # sanity check
```

---

## Phase 1: EVO-HUB v1.0 — Master Dashboard ✅ COMPLETE

**Delivered:** 2026-07-04
**Commit:** `8808121`

### What Was Built
- **React Dashboard**: Live status bar, 7 venture cards, pipeline monitor
- **ITDD Scoreboard**: Per-venture compliance (green/red/gray)
- **Real Action Buttons**: Generate Venture, Run Tests, Cognitive Loop, WOLF Howl, Insights
- **Cognitive Council**: SUPERPOWERS L3 — 4-voice deliberation (Architect, Skeptic, Pragmatist, Creative)
- **Self-Critique**: SUPERPOWERS L4 — Red Team audit, 8 fixes applied
- **M-AI-SELF Bridge**: 4-step integration (bridge, hybrid memory, project binding, OMEGA probe)

### Endpoints (19 total, all 200 OK)
```
/health                           EVO-HUB status
/api/ventures                     7 ventures portfolio
/api/status                       System status (EVO-HUB, LUMEN, Ollama)
/api/pipeline                     Venture-Swarm pipeline
/api/action/generate              Trigger venture generation
/api/action/tests                 Run all test suites
/api/action/cognitive             EVO Agent cognitive loop
/api/action/howl                  WOLF howl
/api/action/insights              NOESIS insights
/api/itdd/status                  ITDD compliance scoreboard
/api/council/deliberate           4-voice council
/api/council/voices               List council roles
/api/mas/health                   M-AI-SELF health
/api/mas/status                   M-AI-SELF status
/api/memory2/status               Hybrid memory status
/api/memory2/search               Semantic search
/api/memory2/episodes             Episodic memories
/api/omega/health                 OMEGA gateway probe
/ws/dashboard                     WebSocket real-time updates
```

---

## Phase 2: EVO-HUB v1.1 — Production Hardening 🔄 IN PROGRESS

**Target:** 2026-07-11
**Goal:** Fix remaining Self-Critique issues, add missing tests, secure for production

### Tasks
| # | Task | Priority | Self-Critique Finding |
|---|------|----------|----------------------|
| 2.1 | Fix remaining `any` in legacy files | HIGH | `src_pages_Charts.tsx`, `src_pages_Tables.tsx` |
| 2.2 | Add skeleton screens for loading states | MEDIUM | Missing placeholder UI during data fetch |
| 2.3 | Add structured logging (winston/pino) | MEDIUM | Console.log in production |
| 2.4 | Add input validation schemas (zod/pydantic) | MEDIUM | No runtime validation on API inputs |
| 2.5 | Add retry logic for fetch calls | MEDIUM | Error handling only logs to console |
| 2.6 | Add tests for 6 missing ventures | HIGH | 6/7 ventures have 0 tests |
| 2.7 | Add E2E tests for Dashboard actions | HIGH | No E2E coverage for Generate/Test/Howl |
| 2.8 | Fix CORS for production domain | CRITICAL | Currently only localhost whitelist |
| 2.9 | Add HTTPS redirect middleware | CRITICAL | Plain HTTP in production |
| 2.10 | Add request logging middleware | MEDIUM | No audit trail for API calls |

### Verification Criteria
- [ ] 0 TypeScript `any` across all `.tsx` files
- [ ] 14/14 ventures have at least 1 test
- [ ] E2E test: generate venture → verify files created → run tests → deploy
- [ ] CORS allows production domain + localhost
- [ ] All API inputs validated (Pydantic models cover 100% of endpoints)
- [ ] Structured logs written to file (not just console)

---

## Phase 3: EVO-HUB v1.2 — Frontend Polish 🎨

**Target:** 2026-07-18
**Goal:** Make dashboard feel premium, add real-time features, mobile-ready

### Tasks
| # | Task | Motivation |
|---|------|-----------|
| 3.1 | Real-time venture generation progress | User sees live pipeline steps during generation |
| 3.2 | Venture detail page (drill-down) | Click venture card → see files, logs, test results |
| 3.3 | Charts page: metrics visualization | CPU, memory, LLM latency from `/api/metrics` |
| 3.4 | Tables page: ventures table with sorting/filtering | Alternative view to card grid |
| 3.5 | Dark/light mode toggle | Open Design token system supports both |
| 3.6 | Mobile responsive layout | Sidebar collapses to hamburger, cards stack |
| 3.7 | Keyboard shortcuts | `g` = generate, `t` = test, `c` = council |
| 3.8 | Toast notifications | Success/error instead of banner only |
| 3.9 | Activity feed | Log of recent actions (who did what when) |
| 3.10 | Search across all ventures | Global search bar |

### Verification Criteria
- [ ] Dashboard works on 375px width (mobile)
- [ ] Real-time updates via WebSocket show pipeline progress
- [ ] All pages have consistent design tokens
- [ ] Keyboard shortcuts documented in `/help` modal

---

## Phase 4: M-AI-SELF Deep Integration 🧠

**Target:** 2026-08-01
**Goal:** Replace local agents with M-AI-SELF agents, share memory, unified cognitive loop

### Tasks
| # | Task | What Changes |
|---|------|-------------|
| 4.1 | Use M-AI-SELF agents instead of local `evo_agent.py` | 5 M-AI-SELF agents (architect, engineer, critic, synthesizer, memory_keeper) |
| 4.2 | Shared episodic memory | EVO-HUB actions stored in M-AI-SELF episodic_store |
| 4.3 | Shared semantic memory | Venture descriptions searchable via M-AI-SELF vector search |
| 4.4 | M-AI-SELF project binding for `noesis-autopilot` repo | Bind to own repo, get module graph + vocabulary |
| 4.5 | M-AI-SELF cognitive loop for venture generation | Replace `venture-swarm.py` subprocess with M-AI-SELF orchestrator |
| 4.6 | Checkpoint system for ventures | Save venture state, rollback if generation fails |
| 4.7 | Cross-world capsules | Share memory between EVO-HUB world and other M-AI-SELF worlds |
| 4.8 | Identity migration | EVO-HUB identity becomes M-AI-SELF world identity |

### Verification Criteria
- [ ] `agents/evo_agent.py` delegates to M-AI-SELF `runtime_loop_async()`
- [ ] All venture data searchable via M-AI-SELF semantic search
- [ ] `noesis-autopilot` repo bound in M-AI-SELF (module graph visible)
- [ ] Venture generation uses M-AI-SELF checkpoint system

---

## Phase 5: OMEGA Activation ⚡

**Target:** 2026-08-15 (when OMEGA gateway is running)
**Goal:** Distributed multi-AI processing for heavy tasks

### Tasks
| # | Task | What It Does |
|---|------|-------------|
| 5.1 | Auto-detect OMEGA gateway | Dashboard shows OMEGA status, nodes count, latency |
| 5.2 | Dispatch heavy generation to OMEGA | Large ventures sent to distributed nodes |
| 5.3 | Parallel model evaluation | Run same prompt on qwen2.5:7b + deepseek-r1 simultaneously, pick best |
| 5.4 | Cross-node memory sync | M-AI-SELF memory replicated across OMEGA nodes |
| 5.5 | Fault-tolerant generation | If one node fails, retry on another |
| 5.6 | Omega-aware Council | Skeptic voice checks if OMEGA nodes available before recommending distributed approach |

### Verification Criteria
- [ ] Dashboard shows "🌐 OMEGA Online — 81 nodes" when gateway running
- [ ] Venture generation completes faster with OMEGA vs single node
- [ ] Council deliberation includes OMEGA availability in Pragmatist reasoning

---

## Phase 6: Productization 🚀

**Target:** 2026-09-01
**Goal:** Package for external users, deployable anywhere, monetizable

### Tasks
| # | Task | Deliverable |
|---|------|-------------|
| 6.1 | One-command install script | `curl -sSL https://.../install.sh \| bash` |
| 6.2 | Docker Compose for full stack | `docker-compose up` starts Ollama + M-AI-SELF + EVO-HUB |
| 6.3 | Environment config wizard | Interactive setup for API keys, model preferences |
| 6.4 | Admin dashboard | User management, resource limits, billing |
| 6.5 | Plugin system | Third-party tools integrate via `action_routes.py` pattern |
| 6.6 | Public venture marketplace | Share ventures, fork, rate, review |
| 6.7 | Documentation site | docs.evo-hub.dev with tutorials, API reference |
| 6.8 | Gumroad / Stripe integration | Paid ventures, premium models, subscription |

### Verification Criteria
- [ ] New user installs and generates first venture in <10 minutes
- [ ] Docker Compose runs all services with single command
- [ ] 3+ external users successfully deploy without help
- [ ] Documentation covers 100% of public API endpoints

---

## Parallel Tracks (Ongoing)

### Security Track
- [ ] Penetration test of all API endpoints
- [ ] Add JWT authentication for production
- [ ] Rate limiting per user (not just IP)
- [ ] Input sanitization for all endpoints
- [ ] Audit log of all actions

### Performance Track
- [ ] Frontend bundle size <200KB (currently unmeasured)
- [ ] API response time <100ms for status endpoints
- [ ] WebSocket reconnection with exponential backoff
- [ ] Lazy loading for venture detail pages
- [ ] CDN for static assets

### Community Track
- [ ] Discord server for users
- [ ] Weekly demo videos
- [ ] Venture template gallery
- [ ] Bug bounty program
- [ ] Contributor guide (CONTRIBUTING.md)

---

## Milestones & Dates

| Milestone | Target | Deliverable |
|-----------|--------|-------------|
| **v1.0** ✅ | 2026-07-04 | Dashboard + M-AI-SELF bridge + Council + Self-Critique |
| **v1.1** | 2026-07-11 | Production hardening, tests, security fixes |
| **v1.2** | 2026-07-18 | Frontend polish, real-time, mobile, charts |
| **v2.0** | 2026-08-01 | M-AI-SELF deep integration (agents, memory, binding) |
| **v2.1** | 2026-08-15 | OMEGA activation (distributed processing) |
| **v3.0** | 2026-09-01 | Productization (install, marketplace, monetization) |

---

## Current Sprint (v1.1)

**Week of:** 2026-07-04 → 2026-07-11

**Focus:** Fix what Self-Critique found, make it production-ready

**Top 3 priorities:**
1. Add tests to 6 missing ventures (HIGH)
2. Fix TypeScript `any` in legacy pages (HIGH)
3. Add input validation to all endpoints (HIGH)

**Definition of Done:**
- All 8 Self-Critique issues from v1.0 are resolved
- New Self-Critique run shows confidence >90%
- E2E test passes: generate → test → deploy

---

## How to Contribute

1. Pick a task from Phase 2 (Production Hardening)
2. Write tests first (ITDD discipline)
3. Run Self-Critique before submitting
4. Update this ROADMAP.md when completing a phase

---

*Last updated: 2026-07-04*
*Version: EVO-DASH v1.0*
*Next review: 2026-07-11*
