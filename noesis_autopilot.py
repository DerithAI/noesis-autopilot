#!/usr/bin/env python3
"""
NOESIS AUTOPILOT — Self-observing, self-remembering, self-deliberating loop.
Standalone version. Drop into any project, run, watch it evolve.

Usage:
    python noesis_autopilot.py
"""

import json
import hashlib
import time
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import sqlite3

# ═══════════════════════════════════════════════════════════════════════════════
# COMPACT EPISODIC MEMORY (SQLite)
# ═══════════════════════════════════════════════════════════════════════════════

class EpisodicStore:
    def __init__(self, db_path: str = "autopilot_memory.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
        self.lock = threading.Lock()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                cycle INTEGER,
                event_type TEXT,
                content TEXT,
                coherence REAL,
                energy REAL
            )
        """)
        self.conn.commit()

    def create(self, cycle: int, event_type: str, content: dict, coherence: float, energy: float):
        with self.lock:
            self.conn.execute(
                "INSERT INTO episodes (timestamp, cycle, event_type, content, coherence, energy) VALUES (?, ?, ?, ?, ?, ?)",
                (datetime.now(timezone.utc).isoformat(), cycle, event_type, json.dumps(content), coherence, energy)
            )
            self.conn.commit()

    def count(self) -> int:
        with self.lock:
            cur = self.conn.execute("SELECT COUNT(*) FROM episodes")
            return cur.fetchone()[0]

    def get_recent(self, n: int = 10):
        with self.lock:
            cur = self.conn.execute(
                "SELECT timestamp, cycle, event_type, content, coherence, energy FROM episodes ORDER BY id DESC LIMIT ?",
                (n,)
            )
            return cur.fetchall()

    def summary(self) -> dict:
        with self.lock:
            cur = self.conn.execute("""
                SELECT COUNT(*), AVG(coherence), AVG(energy), MAX(cycle)
                FROM episodes
            """)
            total, avg_coh, avg_nrg, max_cycle = cur.fetchone()
            return {
                "total_episodes": total or 0,
                "avg_coherence": round(avg_coh or 0, 3),
                "avg_energy": round(avg_nrg or 0, 3),
                "max_cycle": max_cycle or 0,
            }


# ═══════════════════════════════════════════════════════════════════════════════
# LATTICE (in-memory graph)
# ═══════════════════════════════════════════════════════════════════════════════

class CognitiveLattice:
    def __init__(self):
        self.nodes: Dict[str, dict] = {}
        self.edges: List[tuple] = []

    def add_node(self, name: str, type_: str, description: str = "", meta: dict = None):
        self.nodes[name] = {"type": type_, "description": description, "meta": meta or {}}

    def add_edge(self, a: str, b: str, relation: str, weight: float = 1.0):
        self.edges.append((a, b, {"relation": relation, "weight": weight}))

    def get_node(self, name: str) -> Optional[dict]:
        return self.nodes.get(name)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)


# ═══════════════════════════════════════════════════════════════════════════════
# ENERGY SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class EnergySystem:
    def __init__(self, budget: float = 100.0):
        self.budget = budget
        self.remaining = budget
        self.drained = 0.0

    def consume(self, amount: float):
        self.remaining = max(0.0, self.remaining - amount)
        self.drained += amount

    def reward(self, amount: float):
        self.remaining = min(self.budget, self.remaining + amount)

    def status(self) -> dict:
        return {
            "budget": self.budget,
            "remaining": round(self.remaining, 2),
            "drained": round(self.drained, 2),
            "ratio": round(self.remaining / self.budget, 2) if self.budget else 0.0,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# OBSERVER — scans project and environment
# ═══════════════════════════════════════════════════════════════════════════════

class ProjectObserver:
    def __init__(self, root: str = "."):
        self.root = Path(root)
        self.files: List[Path] = []

    def scan(self) -> dict:
        self.files = list(self.root.rglob("*.py"))
        all_files = list(self.root.rglob("*"))
        total_size = sum(f.stat().st_size for f in all_files if f.is_file())
        dirs = [d for d in all_files if d.is_dir() and not any(p.name.startswith(".") for p in d.relative_to(self.root).parents)]
        return {
            "py_files": len(self.files),
            "total_files": len([f for f in all_files if f.is_file()]),
            "directories": len(dirs),
            "total_size_kb": round(total_size / 1024, 1),
            "modules": [f.stem for f in self.files],
            "timestamp": datetime.now().isoformat(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DELIBERATOR — the 6-person Council
# ═══════════════════════════════════════════════════════════════════════════════

class AssemblyOfAgents:
    def __init__(self):
        self.agents = {
            "WATCHER": "observe_and_label",
            "SACRIFICE": "estimate_cost",
            "MEMORY": "index_and_consolidate",
            "LAW": "validate_action",
            "FLOOD": "govern_recovery",
            "EXECUTE": "propose_action",
        }
        self.history: List[dict] = []

    def deliberate(self, observation: dict, energy: dict, lattice: dict, memory: dict) -> dict:
        decisions = []

        # WATCHER: always observing
        decisions.append({"agent": "WATCHER", "action": "observe", "confidence": 1.0})

        # SACRIFICE: estimate cost
        cost = len(str(observation)) * 0.0001 + lattice["edges"] * 0.001
        decisions.append({"agent": "SACRIFICE", "cost": round(cost, 4), "confidence": 0.9})

        # MEMORY: consolidate if large
        if memory["episodic"] > 50:
            decisions.append({"agent": "MEMORY", "action": "consolidate", "confidence": 0.8})
        else:
            decisions.append({"agent": "MEMORY", "action": "continue", "confidence": 1.0})

        # LAW: validate
        if energy["remaining"] < 10:
            decisions.append({"agent": "LAW", "status": "FORBIDDEN", "reason": "energy_too_low", "confidence": 1.0})
        else:
            decisions.append({"agent": "LAW", "status": "allowed", "confidence": 1.0})

        # FLOOD: governance
        if energy["remaining"] < 20 or observation.get("coherence", 1.0) < 0.3:
            decisions.append({"agent": "FLOOD", "action": "attempt_recovery", "confidence": 0.6})
        else:
            decisions.append({"agent": "FLOOD", "action": "continue", "confidence": 1.0})

        # EXECUTE: propose
        if energy["remaining"] < 10:
            exec_decision = "quiesce"
        elif observation.get("coherence", 1.0) < 0.5:
            exec_decision = "renewal"
        else:
            exec_decision = "execute"
        decisions.append({"agent": "EXECUTE", "decision": exec_decision, "confidence": 0.9})

        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "decisions": decisions,
        })

        return {
            "status": (
                "recovered" if any(d["agent"] == "FLOOD" and d["action"] == "attempt_recovery" for d in decisions)
                else "success"
            ),
            "decision": decisions[-1],
            "council_size": 6,
            "confidence": round(sum(d.get("confidence", 0) for d in decisions) / len(decisions), 3),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# AUTOPILOT KERNEL
# ═══════════════════════════════════════════════════════════════════════════════

class AutopilotKernel:
    def __init__(self, root: str = ".", interval: float = 3.0):
        self.root = root
        self.interval = interval
        self.cycle = 0
        self.energy = EnergySystem(budget=200.0)
        self.lattice = CognitiveLattice()
        self.memory = EpisodicStore()
        self.observer = ProjectObserver(root)
        self.council = AssemblyOfAgents()

        # Seed lattice with root node
        self.lattice.add_node("project_root", "domain", "Project root directory")

        # Previous observation snapshot — baseline for the stability component
        self._prev_obs: Optional[dict] = None

    def _coherence(self, observation: dict) -> float:
        energy_ratio = self.energy.status()["ratio"]
        lattice_density = min(self.lattice.edge_count / max(self.lattice.node_count, 1), 1.0)
        memory_filled = min(self.memory.count() / 100, 1.0)
        stability = self._stability(observation)
        return round((energy_ratio * 0.3 + lattice_density * 0.25 + memory_filled * 0.25 + stability * 0.2), 3)

    def _stability(self, observation: dict) -> float:
        """Reward a settled, consistent project state — not raw growth.

        1.0 = nothing changed since the last cycle; decays toward 0.0 with churn.
        Growth is not coherence: a project that doubles its file count in one
        cycle is *less* coherent until the change has been observed and absorbed.
        """
        snapshot = {
            "py_files": observation["py_files"],
            "directories": observation["directories"],
            "total_size_kb": observation["total_size_kb"],
        }
        prev, self._prev_obs = self._prev_obs, snapshot
        if prev is None:
            return 0.5  # first cycle: neutral, nothing to compare against
        churn = 0.0
        for key in ("py_files", "directories", "total_size_kb"):
            base = max(float(prev[key]), 1.0)
            churn += abs(float(snapshot[key]) - float(prev[key])) / base
        return round(max(0.0, 1.0 - min(churn, 1.0)), 3)

    def _state_hash(self, obj: dict) -> str:
        return hashlib.md5(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]

    def _build_lattice_from_files(self, modules: List[str]):
        for mod in modules:
            if not self.lattice.get_node(mod):
                self.lattice.add_node(mod, "module", f"Python module {mod}")
                self.lattice.add_edge("project_root", mod, "contains")

    def _render_dashboard(self, observation: dict, deliberation: dict, action: str):
        coh = observation.get("coherence", 0.5)
        bar_len = 20
        filled = int(coh * bar_len)
        coh_bar = "█" * filled + "░" * (bar_len - filled)
        en = self.energy.status()

        # Clear previous lines trick — just print fresh block
        print(f"\n{'╔' + '═'*58 + '╗'}")
        print(f"{'║' :<2} AUTOPILOT CYCLE #{self.cycle:05d}  {datetime.now().strftime('%H:%M:%S'):>34} {'║':>2}")
        print(f"{'╠' + '═'*58 + '╣'}")
        print(f"{'║' :<2} Coherence  [{coh_bar}] {coh:.2f} {'║':>{43 - bar_len - len(str(coh))}}")
        print(f"{'║' :<2} Energy     {en['remaining']:>6.1f} / {en['budget']:<5.1f}  (used: {en['drained']:.1f}) {'║':>11}")
        print(f"{'║' :<2} Files      {observation['py_files']:>3} py  | {observation['directories']:>3} dirs | {observation['total_size_kb']:>8.1f} kB {'║':>4}")
        print(f"{'║' :<2} Lattice    {self.lattice.node_count:>3} nodes | {self.lattice.edge_count:>3} edges {'║':>18}")
        print(f"{'║' :<2} Memory     {self.memory.count():>3} episodes | Council: {deliberation['council_size']} agents {'║':>7}")
        print(f"{'╠' + '═'*58 + '╣'}")
        print(f"{'║' :<2} Delib: {deliberation['status'].upper():<8} | decision={deliberation['decision']['decision']:<10} | conf={deliberation['confidence']:.2f} {'║':>2}")
        print(f"{'║' :<2} Action: {action:<49} {'║':>1}")
        print(f"{'╚' + '═'*58 + '╝'}")

    def run_once(self) -> bool:
        self.cycle += 1

        # 1. OBSERVE
        obs = self.observer.scan()
        obs["coherence"] = self._coherence(obs)
        state_hash = self._state_hash(obs)

        # 2. ENERGY COST
        cost = len(str(obs)) * 0.0001 + len(self.lattice.edges) * 0.001
        self.energy.consume(cost)

        if self.energy.status()["remaining"] <= 0:
            print(f"\n[!] ENERGY DEPLETED at cycle {self.cycle}. STOP.")
            return False

        # 3. BUILD LATTICE
        self._build_lattice_from_files(obs["modules"])

        # 4. DELIBERATE
        delib = self.council.deliberate(
            observation=obs,
            energy=self.energy.status(),
            lattice={"nodes": self.lattice.node_count, "edges": self.lattice.edge_count},
            memory={"episodic": self.memory.count()},
        )

        # 5. DECIDE ACTION
        action = delib["decision"]["decision"]
        if action == "execute":
            action_str = f"CONTINUE — monitoring {obs['py_files']} files"
            self.energy.reward(2.0)
        elif action == "renewal":
            action_str = "RENEWAL — coherence low, proposing checkpoint"
        elif action == "quiesce":
            action_str = "QUIESCE — energy critical, slowing down"
        else:
            action_str = f"UNKNOWN STATE: {action}"

        # 6. STORE EPISODE
        self.memory.create(
            cycle=self.cycle,
            event_type="autopilot_cycle",
            content={
                "hash": state_hash,
                "files": obs["py_files"],
                "modules": obs["modules"][:10],
                "action": action,
            },
            coherence=obs["coherence"],
            energy=self.energy.status()["remaining"],
        )

        # 7. RENDER
        self._render_dashboard(obs, delib, action_str)

        return True

    def run(self, max_cycles: Optional[int] = None):
        print("\n" + "=" * 60)
        print("  🚀 NOESIS AUTOPILOT — STANDALONE SELF-OBSERVING SYSTEM")
        print("  " + "─" * 56)
        print(f"  Root: {Path(self.root).resolve()}")
        print(f"  Interval: {self.interval}s | Max cycles: {max_cycles or '∞'}")
        print("  Ctrl+C to stop")
        print("=" * 60 + "\n")

        try:
            while True:
                if max_cycles and self.cycle >= max_cycles:
                    break
                if not self.run_once():
                    break
                if self.cycle < max_cycles or not max_cycles:
                    time.sleep(self.interval)
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()

    def shutdown(self):
        summary = self.memory.summary()
        print("\n" + "=" * 60)
        print("  🛑 AUTOPILOT STOPPED")
        print("  " + "─" * 56)
        print(f"  Total cycles:      {self.cycle}")
        print(f"  Episodes stored:   {summary['total_episodes']}")
        print(f"  Avg coherence:     {summary['avg_coherence']}")
        print(f"  Avg energy:        {summary['avg_energy']}")
        print(f"  Lattice nodes:     {self.lattice.node_count}")
        print(f"  Lattice edges:     {self.lattice.edge_count}")
        print(f"  Memory DB:         autopilot_memory.db")
        print("=" * 60)


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NOESIS Autopilot — self-observing AI system")
    parser.add_argument("--root", default=".", help="Project root to observe")
    parser.add_argument("--interval", type=float, default=3.0, help="Seconds between cycles")
    parser.add_argument("--cycles", type=int, default=None, help="Max cycles (default: infinite)")
    args = parser.parse_args()

    kernel = AutopilotKernel(root=args.root, interval=args.interval)
    kernel.run(max_cycles=args.cycles)
