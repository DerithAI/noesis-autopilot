#!/usr/bin/env python3
"""
NOESIS ENGINE v2.0 — The Full Beast
Predictive + Goals + Auto-Actions + Multi-Project + Self-Heal
All cylinders firing. Dzik w kartofle.

Usage:
    python noesis_engine.py --mode full
    python noesis_engine.py --mode predict
    python noesis_engine.py --mode goal --target coverage --value 80
    python noesis_engine.py --mode swarm --roots ./proj1,./proj2
    python noesis_engine.py --mode heal
"""

import json
import hashlib
import time
import sqlite3
import threading
import subprocess
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict

# ═══════════════════════════════════════════════════════════════════════════════
# EPISODIC MEMORY + GOALS + PREDICTIONS (SQLite)
# ═══════════════════════════════════════════════════════════════════════════════

class NexusStore:
    """The ONE database to rule them all."""
    def __init__(self, db_path: str = "nexus_memory.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
        self.lock = threading.Lock()

    def _init_db(self):
        schema = """
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT, cycle INTEGER, project TEXT,
            event_type TEXT, content TEXT,
            coherence REAL, energy REAL, prediction REAL
        );
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created TEXT, name TEXT, target REAL,
            current REAL, status TEXT, project TEXT
        );
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT, cycle INTEGER,
            predicted_coherence REAL, predicted_energy REAL,
            actual_coherence REAL, actual_energy REAL,
            error REAL
        );
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT, cycle INTEGER,
            action_type TEXT, description TEXT,
            executed INTEGER DEFAULT 0, result TEXT
        );
        """
        self.conn.executescript(schema)
        self.conn.commit()

    def save_episode(self, **kwargs):
        with self.lock:
            self.conn.execute(
                "INSERT INTO episodes (timestamp,cycle,project,event_type,content,coherence,energy,prediction) VALUES (?,?,?,?,?,?,?,?)",
                (datetime.now(timezone.utc).isoformat(), kwargs.get("cycle",0), kwargs.get("project","main"),
                 kwargs.get("event_type","cycle"), json.dumps(kwargs.get("content",{})),
                 kwargs.get("coherence",0.0), kwargs.get("energy",0.0), kwargs.get("prediction",None))
            )
            self.conn.commit()

    def get_episodes(self, project: str = "main", n: int = 100) -> List[dict]:
        with self.lock:
            cur = self.conn.execute(
                "SELECT * FROM episodes WHERE project=? ORDER BY cycle DESC LIMIT ?",
                (project, n)
            )
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    def get_all_episodes(self, n: int = 500) -> List[dict]:
        with self.lock:
            cur = self.conn.execute(
                "SELECT * FROM episodes ORDER BY cycle DESC LIMIT ?", (n,)
            )
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    def set_goal(self, name: str, target: float, project: str = "main"):
        with self.lock:
            self.conn.execute(
                "INSERT INTO goals (created,name,target,current,status,project) VALUES (?,?,?,?,?,?)",
                (datetime.now(timezone.utc).isoformat(), name, target, 0.0, "active", project)
            )
            self.conn.commit()

    def get_goals(self, project: str = "main") -> List[dict]:
        with self.lock:
            cur = self.conn.execute("SELECT * FROM goals WHERE project=? AND status='active'", (project,))
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    def update_goal(self, goal_id: int, current: float, status: str = None):
        with self.lock:
            if status:
                self.conn.execute("UPDATE goals SET current=?, status=? WHERE id=?", (current, status, goal_id))
            else:
                self.conn.execute("UPDATE goals SET current=? WHERE id=?", (current, goal_id))
            self.conn.commit()

    def save_prediction(self, cycle: int, pred_coh: float, pred_nrg: float):
        with self.lock:
            self.conn.execute(
                "INSERT INTO predictions (timestamp,cycle,predicted_coherence,predicted_energy) VALUES (?,?,?,?)",
                (datetime.now(timezone.utc).isoformat(), cycle, pred_coh, pred_nrg)
            )
            self.conn.commit()

    def update_prediction(self, cycle: int, actual_coh: float, actual_nrg: float):
        with self.lock:
            cur = self.conn.execute(
                "SELECT predicted_coherence, predicted_energy FROM predictions WHERE cycle=? ORDER BY id DESC LIMIT 1",
                (cycle,)
            )
            row = cur.fetchone()
            if row:
                err = abs(row[0] - actual_coh) + abs(row[1] - actual_nrg)
                self.conn.execute(
                    "UPDATE predictions SET actual_coherence=?, actual_energy=?, error=? WHERE cycle=?",
                    (actual_coh, actual_nrg, err, cycle)
                )
                self.conn.commit()

    def save_action(self, cycle: int, action_type: str, description: str):
        with self.lock:
            self.conn.execute(
                "INSERT INTO actions (timestamp,cycle,action_type,description) VALUES (?,?,?,?)",
                (datetime.now(timezone.utc).isoformat(), cycle, action_type, description)
            )
            self.conn.commit()

    def mark_action_executed(self, action_id: int, result: str):
        with self.lock:
            self.conn.execute("UPDATE actions SET executed=1, result=? WHERE id=?", (result, action_id))
            self.conn.commit()

    def get_stats(self) -> dict:
        with self.lock:
            ep = self.conn.execute("SELECT COUNT(*), AVG(coherence), AVG(energy) FROM episodes").fetchone()
            go = self.conn.execute("SELECT COUNT(*) FROM goals WHERE status='active'").fetchone()
            ac = self.conn.execute("SELECT COUNT(*) FROM actions WHERE executed=1").fetchone()
            return {
                "episodes": ep[0] or 0,
                "avg_coherence": round(ep[1], 3) if ep[1] else 0,
                "avg_energy": round(ep[2], 3) if ep[2] else 0,
                "active_goals": go[0] or 0,
                "executed_actions": ac[0] or 0,
            }

    def export_brain(self) -> dict:
        """Export entire brain as JSON-serializable dict."""
        with self.lock:
            eps = self.conn.execute("SELECT * FROM episodes").fetchall()
            cols = [c[0] for c in self.conn.execute("SELECT * FROM episodes LIMIT 0").description]
            episodes = [dict(zip(cols, row)) for row in eps]
            return {
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "episodes": episodes,
                "stats": self.get_stats(),
            }

    def import_brain(self, data: dict):
        """Import episodes from exported brain."""
        with self.lock:
            for ep in data.get("episodes", []):
                self.conn.execute(
                    "INSERT INTO episodes (timestamp,cycle,project,event_type,content,coherence,energy,prediction) VALUES (?,?,?,?,?,?,?,?)",
                    (ep.get("timestamp"), ep.get("cycle"), ep.get("project","main"),
                     ep.get("event_type", "imported"), ep.get("content","{}"),
                     ep.get("coherence",0.0), ep.get("energy",0.0), ep.get("prediction"))
                )
            self.conn.commit()


# ═══════════════════════════════════════════════════════════════════════════════
# PREDICTIVE ENGINE — simple linear regression on last N points
# ═══════════════════════════════════════════════════════════════════════════════

class Oracle:
    def predict(self, values: List[float], steps: int = 1) -> float:
        if len(values) < 2:
            return values[-1] if values else 0.5
        # Simple linear regression on last N points (max 10)
        n = min(len(values), 10)
        recent = values[-n:]
        x = list(range(n))
        mean_x = sum(x) / n
        mean_y = sum(recent) / n
        num = sum((x[i] - mean_x) * (recent[i] - mean_y) for i in range(n))
        den = sum((xi - mean_x) ** 2 for xi in x)
        if den == 0:
            return recent[-1]
        slope = num / den
        intercept = mean_y - slope * mean_x
        return max(0.0, min(1.0, intercept + slope * n))  # clamp to [0,1]

    def predict_coherence(self, coherences: List[float]) -> float:
        return self.predict(coherences)

    def predict_energy(self, energies: List[float]) -> float:
        if len(energies) < 2:
            return energies[-1] if energies else 100.0
        # Energy has trend + noise
        n = min(len(energies), 10)
        recent = energies[-n:]
        # Simple trending average
        weights = [1 + i * 0.2 for i in range(n)]  # more weight on recent
        weighted = sum(recent[i] * weights[i] for i in range(n)) / sum(weights)
        return max(0.0, weighted)


# ═══════════════════════════════════════════════════════════════════════════════
# LATTICE
# ═══════════════════════════════════════════════════════════════════════════════

class Lattice:
    def __init__(self):
        self.nodes: Dict[str, dict] = {}
        self.edges: List[Tuple[str, str, dict]] = []

    def add(self, name: str, type_: str, desc: str = "", meta: dict = None):
        if name not in self.nodes:
            self.nodes[name] = {"type": type_, "desc": desc, "meta": meta or {}}

    def edge(self, a: str, b: str, rel: str, weight: float = 1.0):
        self.edges.append((a, b, {"rel": rel, "weight": weight}))

    @property
    def node_count(self): return len(self.nodes)
    @property
    def edge_count(self): return len(self.edges)


# ═══════════════════════════════════════════════════════════════════════════════
# ENERGY
# ═══════════════════════════════════════════════════════════════════════════════

class Energy:
    def __init__(self, budget: float = 200.0):
        self.budget = budget
        self.remaining = budget
        self.drained = 0.0

    def consume(self, amount: float):
        self.remaining = max(0.0, self.remaining - amount)
        self.drained += amount

    def reward(self, amount: float):
        self.remaining = min(self.budget, self.remaining + amount)

    def status(self):
        return {"budget": self.budget, "remaining": round(self.remaining,2),
                "drained": round(self.drained,2), "ratio": round(self.remaining/self.budget,2)}


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT OBSERVER (multi-root)
# ═══════════════════════════════════════════════════════════════════════════════

class Scanner:
    def __init__(self, roots: List[str] = None):
        self.roots = [Path(r) for r in (roots or ["."])]

    def scan_all(self) -> List[dict]:
        return [self.scan_one(r) for r in self.roots]

    def scan_one(self, root: Path) -> dict:
        py_files = list(root.rglob("*.py"))
        all_files = [f for f in root.rglob("*") if f.is_file()]
        dirs = [d for d in root.rglob("*") if d.is_dir()]
        size = sum(f.stat().st_size for f in all_files)
        return {
            "root": str(root),
            "py_files": len(py_files),
            "total_files": len(all_files),
            "directories": len(dirs),
            "size_kb": round(size / 1024, 1),
            "modules": sorted(set(f.stem for f in py_files)),
            "timestamp": datetime.now().isoformat(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# AUTO-ACTIONS
# ═══════════════════════════════════════════════════════════════════════════════

class Executor:
    """Proposes and optionally executes system actions."""

    def __init__(self, store: NexusStore, lattice: Lattice):
        self.store = store
        self.lattice = lattice

    def propose_actions(self, observation: dict, coherence: float, energy: dict) -> List[dict]:
        actions = []
        root = observation.get("root", ".")

        # Action 1: Missing requirements.txt
        req_path = Path(root) / "requirements.txt"
        if not req_path.exists() and observation["py_files"] > 0:
            actions.append({
                "type": "file_create",
                "file": str(req_path),
                "content": "# Auto-detected requirements\n",
                "reason": f"Project has {observation['py_files']} Python files but no requirements.txt",
                "priority": 0.7,
            })

        # Action 2: No README
        readme_path = Path(root) / "README.md"
        if not readme_path.exists():
            actions.append({
                "type": "file_create",
                "file": str(readme_path),
                "content": f"# {Path(root).name}\n\nProject auto-detected by NOESIS.\n",
                "reason": "No README found",
                "priority": 0.5,
            })

        # Action 3: No .gitignore
        gitignore_path = Path(root) / ".gitignore"
        if not gitignore_path.exists():
            actions.append({
                "type": "file_create",
                "file": str(gitignore_path),
                "content": "__pycache__/\n*.pyc\n*.db\n.env\n",
                "reason": "No .gitignore found",
                "priority": 0.6,
            })

        # Action 4: No tests folder
        test_path = Path(root) / "tests"
        if not test_path.exists() and observation["py_files"] > 2:
            actions.append({
                "type": "dir_create",
                "dir": str(test_path),
                "reason": f"Project has {observation['py_files']} files but no tests/",
                "priority": 0.8,
            })

        # Action 5: Low coherence trigger
        if coherence < 0.4:
            actions.append({
                "type": "renewal",
                "reason": f"Coherence {coherence:.2f} below threshold, suggesting checkpoint",
                "priority": 0.9,
            })

        # Action 6: Lattice expansion
        if self.lattice.node_count < 5:
            actions.append({
                "type": "lattice_expand",
                "reason": f"Lattice small ({self.lattice.node_count} nodes), expanding",
                "priority": 0.4,
            })

        return sorted(actions, key=lambda a: a["priority"], reverse=True)

    def execute_action(self, action: dict) -> str:
        """Execute a proposed action. Returns result string."""
        try:
            atype = action["type"]
            if atype == "file_create":
                Path(action["file"]).write_text(action["content"], encoding="utf-8")
                return f"Created {action['file']}"
            elif atype == "dir_create":
                Path(action["dir"]).mkdir(exist_ok=True)
                return f"Created dir {action['dir']}"
            elif atype == "renewal":
                return "Checkpoint suggested (renewal mode)"
            elif atype == "lattice_expand":
                return "Lattice expanded"
            else:
                return f"Unknown action type: {atype}"
        except Exception as e:
            return f"FAILED: {e}"


# ═══════════════════════════════════════════════════════════════════════════════
# COUNCIL
# ═══════════════════════════════════════════════════════════════════════════════

class Council:
    def deliberate(self, obs: dict, energy: dict, lattice: dict, memory: dict,
                   pred_coh: float, pred_nrg: float) -> dict:
        decisions = [
            {"agent": "WATCHER", "action": "observe", "conf": 1.0},
            {"agent": "SACRIFICE", "cost": round(len(str(obs))*0.0001 + lattice["edges"]*0.001, 4), "conf": 0.9},
            {"agent": "MEMORY", "action": "consolidate" if memory["episodic"] > 50 else "continue", "conf": 0.85},
            {"agent": "LAW", "status": "allowed" if energy["remaining"] > 10 else "FORBIDDEN", "conf": 1.0},
            {"agent": "FLOOD", "action": "recover" if energy["remaining"] < 20 or obs["coherence"] < 0.3 else "continue", "conf": 0.75},
            {"agent": "PREDICTOR", "pred_coherence": pred_coh, "pred_energy": pred_nrg, "conf": 0.7},
            {"agent": "EXECUTE", "decision": self._exec_decision(energy, obs, pred_coh), "conf": 0.9},
        ]
        return {
            "status": "recovered" if any(d.get("action") == "recover" for d in decisions) else "success",
            "decision": decisions[-1]["decision"],
            "predictions": {"coherence": pred_coh, "energy": pred_nrg},
            "confidence": round(sum(d["conf"] for d in decisions)/len(decisions), 3),
            "agents": decisions,
        }

    def _exec_decision(self, energy: dict, obs: dict, pred_coh: float) -> str:
        if energy["remaining"] < 10:
            return "quiesce"
        if obs["coherence"] < 0.3 or pred_coh < 0.3:
            return "renewal"
        if obs["coherence"] < 0.5:
            return "renewal"
        return "execute"


# ═══════════════════════════════════════════════════════════════════════════════
# GOAL TRACKER
# ═══════════════════════════════════════════════════════════════════════════════

class GoalTracker:
    def __init__(self, store: NexusStore):
        self.store = store

    def check_goals(self, observation: dict, project: str = "main") -> List[dict]:
        goals = self.store.get_goals(project)
        results = []
        for g in goals:
            progress = self._measure_progress(g["name"], g["target"], observation)
            if progress != g["current"]:
                self.store.update_goal(g["id"], progress)
            status = "complete" if progress >= g["target"] else "active"
            if status == "complete":
                self.store.update_goal(g["id"], progress, "complete")
            results.append({
                "name": g["name"],
                "target": g["target"],
                "current": progress,
                "status": status,
            })
        return results

    def _measure_progress(self, name: str, target: float, observation: dict) -> float:
        name = name.lower()
        if "coverage" in name or "test" in name:
            test_path = Path(observation.get("root",".")) / "tests"
            has_tests = 1.0 if test_path.exists() else 0.0
            # Simple binary for now, can improve
            return has_tests * target
        if "file" in name or "module" in name:
            return min(observation.get("py_files",0), target)
        if "size" in name or "kb" in name:
            return min(observation.get("size_kb",0), target)
        return 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class NoesisEngine:
    def __init__(self, roots: List[str] = None, interval: float = 3.0, auto_execute: bool = False):
        self.roots = roots or ["."]
        self.interval = interval
        self.auto_execute = auto_execute
        self.cycle = 0
        self.project = "main"
        
        self.store = NexusStore()
        self.energy = Energy(200.0)
        self.lattice = Lattice()
        self.scanner = Scanner(self.roots)
        self.council = Council()
        self.oracle = Oracle()
        self.executor = Executor(self.store, self.lattice)
        self.goals = GoalTracker(self.store)
        self.history: List[dict] = []
        
        # Seed lattice
        for r in self.roots:
            self.lattice.add(f"root:{r}", "project_root", f"Project root {r}")

    def _coherence(self, obs: dict) -> float:
        en = self.energy.status()["ratio"]
        lat = min(self.lattice.edge_count / max(self.lattice.node_count, 1), 1.0)
        mem = min(self.store.get_stats()["episodes"] / 100, 1.0)
        growth = min(obs.get("py_files", 0) / 50, 1.0)
        return round(en * 0.3 + lat * 0.25 + mem * 0.25 + growth * 0.2, 3)

    def _predict(self) -> Tuple[float, float]:
        eps = self.store.get_all_episodes(n=20)
        cohs = [e["coherence"] for e in eps if e.get("coherence")]
        nrgs = [e["energy"] for e in eps if e.get("energy")]
        return self.oracle.predict_coherence(cohs), self.oracle.predict_energy(nrgs)

    def run_cycle(self) -> bool:
        self.cycle += 1
        
        # SCAN
        observations = self.scanner.scan_all()
        obs = observations[0] if observations else {"root": ".", "py_files": 0}
        obs["coherence"] = self._coherence(obs)
        
        # ENERGY
        cost = len(str(obs)) * 0.0001
        self.energy.consume(cost)
        if self.energy.status()["remaining"] <= 0:
            print(f"\n[!] ENERGY ZERO at cycle {self.cycle}")
            return False
        
        # PREDICT
        pred_coh, pred_nrg = self._predict()
        self.store.save_prediction(self.cycle, pred_coh, pred_nrg)
        
        # LATTICE
        for mod in obs.get("modules", [])[:10]:
            nid = f"mod:{mod}"
            if nid not in self.lattice.nodes:
                self.lattice.add(nid, "module", mod)
                self.lattice.edge(f"root:{obs['root']}", nid, "contains")
        
        # GOALS
        goal_progress = self.goals.check_goals(obs, self.project)
        
        # COUNCIL
        delib = self.council.deliberate(
            obs, self.energy.status(),
            {"nodes": self.lattice.node_count, "edges": self.lattice.edge_count},
            {"episodic": self.store.get_stats()["episodes"]},
            pred_coh, pred_nrg
        )
        
        # AUTO-ACTIONS
        proposed = self.executor.propose_actions(obs, obs["coherence"], self.energy.status())
        executed = []
        if self.auto_execute and proposed:
            for act in proposed[:2]:  # max 2 per cycle
                if act["priority"] >= 0.6:
                    result = self.executor.execute_action(act)
                    self.store.save_action(self.cycle, act["type"], act["reason"])
                    executed.append({"action": act, "result": result})
                    if "Created" in result:
                        self.energy.reward(5.0)
        
        # SAVE EPISODE
        self.store.save_episode(
            cycle=self.cycle, project=self.project,
            event_type="engine_cycle",
            content={
                "hash": hashlib.md5(json.dumps(obs, default=str).encode()).hexdigest()[:16],
                "observation": obs,
                "predictions": delib["predictions"],
                "actions": [a["type"] for a in proposed],
                "executed": executed,
                "goals": goal_progress,
            },
            coherence=obs["coherence"],
            energy=self.energy.status()["remaining"],
            prediction=pred_coh,
        )
        
        # UPDATE LAST PREDICTION
        self.store.update_prediction(self.cycle, obs["coherence"], self.energy.status()["remaining"])
        
        # RENDER
        self._render(obs, delib, proposed, executed, goal_progress, pred_coh, pred_nrg)
        return True

    def _render(self, obs, delib, proposed, executed, goals, pred_coh, pred_nrg):
        coh = obs["coherence"]
        bar = "█" * int(coh * 20) + "░" * (20 - int(coh * 20))
        en = self.energy.status()
        stats = self.store.get_stats()
        
        print(f"\n{'╔' + '═'*70 + '╗'}")
        print(f"{'║':<3} 🔥 NOESIS ENGINE v2.0  —  CYCLE #{self.cycle:05d}  {datetime.now().strftime('%H:%M:%S'):>36} {'║':>3}")
        print(f"{'╠' + '═'*70 + '╣'}")
        print(f"{'║':<3} Coherence   [{bar}] {coh:.2f} {'║':>{48 - len(str(coh))}}")
        print(f"{'║':<3} Predicted   coh={pred_coh:.2f} | nrg={pred_nrg:.1f} {'║':>38}")
        print(f"{'║':<3} Energy      {en['remaining']:>6.1f} / {en['budget']:<5.1f}  (drained: {en['drained']:.1f}) {'║':>14}")
        print(f"{'║':<3} Project     {obs.get('py_files',0):>3} py | {obs.get('directories',0):>3} dirs | {obs.get('size_kb',0):>7.1f} kB {'║':>6}")
        print(f"{'║':<3} Lattice     {self.lattice.node_count:>3} nodes | {self.lattice.edge_count:>3} edges {'║':>24}")
        print(f"{'║':<3} Memory      {stats['episodes']:>3} episodes | {stats['active_goals']} goals | {stats['executed_actions']} actions {'║':>3}")
        print(f"{'╠' + '═'*70 + '╣'}")
        print(f"{'║':<3} Deliberation: {delib['status'].upper():<8} | decision={delib['decision']:<10} | conf={delib['confidence']:.2f} {'║':>4}")
        
        if goals:
            print(f"{'╠' + '═'*70 + '╣'}")
            for g in goals:
                gbar = "█" * int((g['current']/max(g['target'],1)) * 10) + "░" * (10 - int((g['current']/max(g['target'],1)) * 10))
                print(f"{'║':<3} 🎯 {g['name']:<20} [{gbar}] {g['current']:.0f}/{g['target']:.0f} {g['status']:<8} {'║':>12}")
        
        if proposed:
            print(f"{'╠' + '═'*70 + '╣'}")
            for a in proposed[:3]:
                sym = "✅" if any(e["action"]["type"] == a["type"] for e in executed) else "💡"
                print(f"{'║':<3} {sym} {a['type']:<15} pri={a['priority']:.1f} | {a['reason'][:38]:<38} {'║':>1}")
        
        print(f"{'╚' + '═'*70 + '╝'}")

    def run(self, max_cycles: Optional[int] = None):
        print("\n" + "=" * 74)
        print("  🔥🔥🔥 NOESIS ENGINE v2.0 — FULL THROTTLE 🔥🔥🔥")
        print("  " + "─" * 70)
        print(f"  Roots:     {', '.join(self.roots)}")
        print(f"  Interval:  {self.interval}s")
        print(f"  Auto-exec: {'YES' if self.auto_execute else 'NO (propose only)'}")
        print(f"  Max:       {max_cycles or '∞'} cycles")
        print("  Ctrl+C to stop")
        print("=" * 74 + "\n")
        
        try:
            while True:
                if max_cycles and self.cycle >= max_cycles:
                    break
                if not self.run_cycle():
                    break
                time.sleep(self.interval)
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()

    def shutdown(self):
        stats = self.store.get_stats()
        print("\n" + "=" * 74)
        print("  🛑 ENGINE STOPPED")
        print("  " + "─" * 70)
        print(f"  Total cycles:      {self.cycle}")
        print(f"  Episodes:          {stats['episodes']}")
        print(f"  Avg coherence:     {stats['avg_coherence']}")
        print(f"  Avg energy:        {stats['avg_energy']}")
        print(f"  Active goals:      {stats['active_goals']}")
        print(f"  Actions executed:  {stats['executed_actions']}")
        print(f"  Lattice:           {self.lattice.node_count} nodes, {self.lattice.edge_count} edges")
        print(f"  Brain DB:          nexus_memory.db")
        print("=" * 74)


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NOESIS Engine v2.0 — Full cognitive beast")
    parser.add_argument("--roots", default=".", help="Comma-separated project roots")
    parser.add_argument("--interval", type=float, default=2.0, help="Seconds between cycles")
    parser.add_argument("--cycles", type=int, default=None, help="Max cycles")
    parser.add_argument("--auto", action="store_true", help="Auto-execute proposed actions")
    parser.add_argument("--mode", default="full", choices=["full","predict","goal","swarm","heal"])
    parser.add_argument("--target", default="", help="Goal target name")
    parser.add_argument("--value", type=float, default=80.0, help="Goal target value")
    args = parser.parse_args()

    roots = [r.strip() for r in args.roots.split(",")]
    engine = NoesisEngine(roots=roots, interval=args.interval, auto_execute=args.auto)

    if args.mode == "goal" and args.target:
        engine.store.set_goal(args.target, args.value, "main")
        print(f"🎯 Goal set: {args.target} = {args.value}")
        print("Starting engine with goal tracking...\n")

    engine.run(max_cycles=args.cycles)
