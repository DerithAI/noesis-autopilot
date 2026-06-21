#!/usr/bin/env python3
"""
NOESIS DASHBOARD — Live web dashboard + memory export + Hermes watcher
Standalone HTTP server. Zero dependencies (stdlib only).

Usage:
    python noesis_dashboard.py           # Start dashboard on :8080
    python noesis_dashboard.py --port 3000  # Custom port
    python noesis_dashboard.py --watch   # Watch Hermes for triggers
"""

import json
import sqlite3
import threading
import time
import urllib.request
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, List

# ═══════════════════════════════════════════════════════════════════════════════
# MEMORY CONNECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class BrainConnector:
    def __init__(self, db_path: str = "nexus_memory.db"):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def get_latest(self, n: int = 50) -> List[dict]:
        conn = self._connect()
        try:
            cur = conn.execute("SELECT * FROM episodes ORDER BY id DESC LIMIT ?", (n,))
            cols = [c[0] for c in cur.description]
            rows = [dict(zip(cols, row)) for row in cur.fetchall()]
            for r in rows:
                try:
                    r["content"] = json.loads(r["content"])
                except Exception:
                    pass
            return rows
        finally:
            conn.close()

    def get_goals(self) -> List[dict]:
        conn = self._connect()
        try:
            cur = conn.execute("SELECT * FROM goals WHERE status='active' ORDER BY id DESC")
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
        finally:
            conn.close()

    def get_predictions(self, n: int = 20) -> List[dict]:
        conn = self._connect()
        try:
            cur = conn.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT ?", (n,))
            cols = [c[0] for c in cur.description]
            rows = [dict(zip(cols, row)) for row in cur.fetchall()]
            return rows
        finally:
            conn.close()

    def get_stats(self) -> dict:
        conn = self._connect()
        try:
            ep = conn.execute("SELECT COUNT(*), AVG(coherence), AVG(energy) FROM episodes").fetchone()
            go = conn.execute("SELECT COUNT(*) FROM goals WHERE status='active'").fetchone()
            ac = conn.execute("SELECT COUNT(*) FROM actions WHERE executed=1").fetchone()
            pr = conn.execute("SELECT AVG(error) FROM predictions WHERE error IS NOT NULL").fetchone()
            return {
                "episodes": ep[0] or 0,
                "avg_coherence": round(ep[1] or 0, 3),
                "avg_energy": round(ep[2] or 0, 3),
                "active_goals": go[0] or 0,
                "executed_actions": ac[0] or 0,
                "prediction_error": round(pr[0] or 0, 4),
            }
        finally:
            conn.close()

    def export_json(self) -> dict:
        conn = self._connect()
        try:
            tables = ["episodes", "goals", "predictions", "actions"]
            data = {}
            for t in tables:
                cur = conn.execute(f"SELECT * FROM {t}")
                cols = [c[0] for c in cur.description]
                rows = [dict(zip(cols, row)) for row in cur.fetchall()]
                for r in rows:
                    for k, v in r.items():
                        if isinstance(v, (datetime,)):
                            r[k] = v.isoformat()
                data[t] = rows
            return {
                "exported_at": datetime.now().isoformat(),
                "tables": data,
                "stats": self.get_stats(),
            }
        finally:
            conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# HERMES WATCHER — poll for triggers from Hermes
# ═══════════════════════════════════════════════════════════════════════════════

class HermesWatcher:
    def __init__(self, callback, interval: float = 5.0):
        self.callback = callback
        self.interval = interval
        self.running = False
        self.thread = None
        self.last_check = 0

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print(f"[WATCHER] Hermes watcher started (interval={self.interval}s)")

    def stop(self):
        self.running = False

    def _loop(self):
        while self.running:
            self._check()
            time.sleep(self.interval)

    def _check(self):
        """Check for trigger files or simple heuristics."""
        trigger_path = Path(".noesis_trigger")
        if trigger_path.exists() and trigger_path.stat().st_mtime > self.last_check:
            self.last_check = trigger_path.stat().st_mtime
            content = trigger_path.read_text().strip()
            self.callback(type="trigger", content=content)


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

class DashboardHandler(BaseHTTPRequestHandler):
    brain: BrainConnector = None

    def log_message(self, format, *args):
        pass  # Suppress logs

    def _json_response(self, data: dict, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, default=str).encode())

    def _html_response(self, html: str, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_GET(self):
        if self.path == "/" or self.path == "/dashboard":
            self._serve_dashboard()
        elif self.path == "/api/stats":
            self._json_response(self.brain.get_stats())
        elif self.path == "/api/episodes":
            self._json_response({"episodes": self.brain.get_latest(50)})
        elif self.path == "/api/goals":
            self._json_response({"goals": self.brain.get_goals()})
        elif self.path == "/api/predictions":
            self._json_response({"predictions": self.brain.get_predictions(20)})
        elif self.path == "/api/export":
            data = self.brain.export_json()
            # Also save to file
            Path("noesis_brain_export.json").write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
            self._json_response({"exported": True, "path": "noesis_brain_export.json", "stats": data["stats"]})
        elif self.path == "/api/brain":
            self._json_response(self.brain.export_json())
        else:
            self.send_error(404)

    def _serve_dashboard(self):
        html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>NOESIS Dashboard</title>
<style>
:root { --bg:#0a0a12; --card:#12121e; --accent:#ff6b35; --green:#00d26a; --blue:#4facfe; --text:#e0e0e0; --muted:#888; }
body { margin:0; background:var(--bg); color:var(--text); font-family:system-ui,-apple-system,sans-serif; }
.header { background:linear-gradient(135deg,#1a1a2e,#16213e); padding:20px 30px; border-bottom:2px solid var(--accent); }
.header h1 { margin:0; font-size:28px; color:var(--accent); }
.header .subtitle { color:var(--muted); font-size:14px; margin-top:5px; }
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:15px; padding:20px 30px; }
.card { background:var(--card); border-radius:12px; padding:20px; border:1px solid #222; }
.card h3 { margin:0 0 15px; font-size:16px; color:var(--blue); text-transform:uppercase; letter-spacing:1px; }
.stat-big { font-size:42px; font-weight:800; color:var(--accent); }
.stat-label { color:var(--muted); font-size:12px; text-transform:uppercase; }
.bar { background:#1e1e30; height:10px; border-radius:5px; overflow:hidden; margin-top:10px; }
.bar-fill { height:100%; background:linear-gradient(90deg,var(--accent),var(--green)); transition:width 0.5s; }
.timeline { padding:20px 30px; }
.timeline h3 { color:var(--blue); }
.episode { display:flex; gap:15px; padding:10px 15px; background:var(--card); border-radius:8px; margin-bottom:8px; border-left:3px solid var(--accent); }
.episode.cycle-high { border-left-color:var(--green); }
.episode.cycle-low { border-left-color:#ff4444; }
.ep-meta { min-width:80px; color:var(--muted); font-size:12px; }
.ep-data { flex:1; }
.ep-action { font-size:13px; color:var(--muted); }
.meter { display:flex; align-items:center; gap:10px; margin:8px 0; }
.meter-label { min-width:100px; font-size:12px; color:var(--muted); }
.refresh { position:fixed; bottom:20px; right:20px; background:var(--accent); color:#fff; border:none; padding:12px 24px; border-radius:30px; font-weight:bold; cursor:pointer; }
.refresh:hover { transform:scale(1.05); }
.goals { display:flex; gap:10px; flex-wrap:wrap; }
.goal-badge { background:linear-gradient(135deg,#1a1a2e,#16213e); padding:8px 16px; border-radius:20px; border:1px solid var(--blue); font-size:13px; }
.goal-badge.done { border-color:var(--green); color:var(--green); }
#chart { width:100%; height:200px; background:var(--card); border-radius:8px; margin-top:15px; }
</style>
</head>
<body>
<div class="header">
  <h1>🧠 NOESIS Dashboard</h1>
  <div class="subtitle">Live cognitive state | <span id="clock"></span></div>
</div>

<div class="grid">
  <div class="card">
    <h3>🔄 Cycles</h3>
    <div class="stat-big" id="stat-cycles">-</div>
    <div class="stat-label">Total episodes observed</div>
  </div>
  <div class="card">
    <h3>🧿 Coherence</h3>
    <div class="stat-big" id="stat-coherence">-</div>
    <div class="stat-label">Average system coherence</div>
    <div class="bar"><div class="bar-fill" id="bar-coh" style="width:0%"></div></div>
  </div>
  <div class="card">
    <h3>⚡ Energy</h3>
    <div class="stat-big" id="stat-energy">-</div>
    <div class="stat-label">Average energy level</div>
  </div>
  <div class="card">
    <h3>🎯 Goals</h3>
    <div class="stat-big" id="stat-goals">-</div>
    <div class="stat-label">Active goals tracked</div>
    <div class="goals" id="goals-list"></div>
  </div>
  <div class="card">
    <h3>📊 Predictions</h3>
    <div class="stat-big" id="stat-pred">-</div>
    <div class="stat-label">Prediction error (avg)</div>
  </div>
  <div class="card">
    <h3>⚙️ Actions</h3>
    <div class="stat-big" id="stat-actions">-</div>
    <div class="stat-label">Auto-executed actions</div>
  </div>
</div>

<div class="timeline">
  <h3>📜 Recent Episodes</h3>
  <div id="episodes"></div>
</div>

<button class="refresh" onclick="loadAll()">🔄 Refresh</button>

<script>
function fmt(n) { return n !== undefined && n !== null ? Number(n).toFixed(2) : '-'; }

async function loadStats() {
  const r = await fetch('/api/stats');
  const s = await r.json();
  document.getElementById('stat-cycles').textContent = s.episodes;
  document.getElementById('stat-coherence').textContent = fmt(s.avg_coherence);
  document.getElementById('stat-energy').textContent = fmt(s.avg_energy);
  document.getElementById('stat-goals').textContent = s.active_goals;
  document.getElementById('stat-pred').textContent = fmt(s.prediction_error);
  document.getElementById('stat-actions').textContent = s.executed_actions;
  const coh = s.avg_coherence || 0;
  document.getElementById('bar-coh').style.width = Math.min(100, coh * 100) + '%';
}

async function loadEpisodes() {
  const r = await fetch('/api/episodes');
  const d = await r.json();
  const container = document.getElementById('episodes');
  container.innerHTML = '';
  d.episodes.slice(0, 10).forEach(ep => {
    const cls = ep.coherence > 0.5 ? 'cycle-high' : (ep.coherence < 0.3 ? 'cycle-low' : '');
    const content = typeof ep.content === 'string' ? JSON.parse(ep.content) : ep.content;
    const actions = content && content.actions ? content.actions.join(', ') : 'observe';
    const div = document.createElement('div');
    div.className = 'episode ' + cls;
    div.innerHTML = `
      <div class="ep-meta">#${String(ep.cycle).padStart(5,'0')}<br>${ep.timestamp ? ep.timestamp.slice(11,19) : '--:--:--'}</div>
      <div class="ep-data">
        <strong>C:${fmt(ep.coherence)} E:${fmt(ep.energy)}</strong>
        <span class="ep-action"> | ${actions}</span>
      </div>`;
    container.appendChild(div);
  });
}

async function loadGoals() {
  const r = await fetch('/api/goals');
  const d = await r.json();
  const list = document.getElementById('goals-list');
  list.innerHTML = '';
  d.goals.forEach(g => {
    const badge = document.createElement('span');
    badge.className = 'goal-badge ' + (g.status === 'complete' ? 'done' : '');
    badge.textContent = `${g.name}: ${Number(g.current).toFixed(0)}/${Number(g.target).toFixed(0)}`;
    list.appendChild(badge);
  });
}

function updateClock() {
  document.getElementById('clock').textContent = new Date().toLocaleTimeString();
}

async function loadAll() {
  await loadStats();
  await loadEpisodes();
  await loadGoals();
}

loadAll();
setInterval(loadAll, 5000);
setInterval(updateClock, 1000);
updateClock();
</script>
</body>
</html>"""
        self._html_response(html)


class DashboardServer:
    def __init__(self, port: int = 8080, db_path: str = "nexus_memory.db"):
        self.port = port
        self.brain = BrainConnector(db_path)
        DashboardHandler.brain = self.brain
        self.server = HTTPServer(("", port), DashboardHandler)
        self.watcher = HermesWatcher(self._on_trigger)
        self.running = False

    def _on_trigger(self, type_: str, content: str):
        print(f"\n🔔 HERMES TRIGGER: {content}")

    def start(self):
        self.running = True
        print(f"\n{'='*60}")
        print(f"  🌐 NOESIS DASHBOARD LIVE")
        print(f"  {'─'*56}")
        print(f"  URL: http://localhost:{self.port}/")
        print(f"  API: http://localhost:{self.port}/api/stats")
        print(f"  Export: http://localhost:{self.port}/api/export")
        print(f"  Press Ctrl+C to stop")
        print(f"{'='*60}")
        self.watcher.start()
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self):
        self.running = False
        self.watcher.stop()
        self.server.shutdown()
        print("\n  Dashboard stopped.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--db", default="nexus_memory.db")
    parser.add_argument("--watch", action="store_true", help="Watch for Hermes triggers")
    args = parser.parse_args()

    server = DashboardServer(port=args.port, db_path=args.db)
    server.start()
