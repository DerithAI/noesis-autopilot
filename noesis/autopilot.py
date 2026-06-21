#!/usr/bin/env python3
"""
NOESIS AUTOPILOT — Self-observing, self-remembering, self-deliberating loop.
The system watches itself, learns from its own state, and proposes actions.
"""
import time
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from noesis import NoesisKernel
from noesis.tools.filesystem import FileSystemTool
from noesis.tools.python_exec import PythonExecTool
from noesis.db.repository import EpisodicRepository
from noesis.vector.store import VectorStore


class NoesisAutopilot:
    """
    Autonomous observation-deliberation-action loop.
    """

    def __init__(self, kernel: NoesisKernel, interval: float = 5.0):
        self.kernel = kernel
        self.interval = interval
        self.fs = FileSystemTool(base_path=".")
        self.python = PythonExecTool()
        self.episodic = EpisodicRepository(kernel._db)
        self.vector = VectorStore()
        self.cycle_count = 0
        self.last_state_hash = ""

    def _scan_project(self) -> Dict[str, Any]:
        """Scan project files and return snapshot."""
        files = self.fs.list_dir(".", pattern="*.py")
        dirs = self.fs.list_dir(".")
        total_size = sum(f["size"] for f in files)
        return {
            "py_files": len(files),
            "directories": len([d for d in dirs if d["is_dir"]]),
            "total_size": total_size,
            "timestamp": datetime.now().isoformat(),
        }

    def _observe(self) -> Dict[str, Any]:
        """Observe current system state."""
        project = self._scan_project()
        energy = self.kernel.energy.status()
        lattice = {
            "nodes": self.kernel.lattice.node_count,
            "edges": self.kernel.lattice.edge_count,
        }
        memory = {
            "episodic": len(self.kernel.memory.episodic_memory),
            "semantic_db": self.vector.count(),
            "reflections": len(self.kernel.memory.reflection_log),
        }
        return {
            "project": project,
            "energy": energy,
            "lattice": lattice,
            "memory": memory,
            "coherence": self._estimate_coherence(),
        }

    def _estimate_coherence(self) -> float:
        """Estimate system coherence based on multiple factors."""
        e = self.kernel.energy.status()
        energy_ratio = e["remaining"] / e["budget"]
        lattice_density = min(self.kernel.lattice.edge_count / max(self.kernel.lattice.node_count, 1), 1.0)
        memory_filled = min(self.vector.count() / 100, 1.0)
        return round((energy_ratio * 0.4 + lattice_density * 0.3 + memory_filled * 0.3), 3)

    def _state_hash(self, state: Dict[str, Any]) -> str:
        """Hash of current state for change detection."""
        raw = json.dumps(state, sort_keys=True, default=str)
        return hashlib.md5(raw.encode()).hexdigest()[:16]

    def _store_observation(self, state: Dict[str, Any]) -> None:
        """Store observation in episodic memory."""
        self.episodic.create(
            event_type="autopilot_observation",
            content={
                "cycle": self.cycle_count,
                "state": state,
                "files": state["project"]["py_files"],
                "coherence": state["coherence"],
            },
            confidence=state["coherence"],
            source="autopilot",
        )

    def _deliberate(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run cognitive cycle on current state."""
        context = {
            "observation": f"Cycle {self.cycle_count}",
            "files": state["project"]["py_files"],
            "coherence": state["coherence"],
            "energy": state["energy"]["remaining"],
            "nodes": state["lattice"]["nodes"],
            "memory": state["memory"]["episodic"],
        }
        return self.kernel.run_cycle(context)

    def _propose_action(self, state: Dict[str, Any], deliberation: Dict[str, Any]) -> Optional[str]:
        """Propose next action based on observation and deliberation."""
        actions = []
        
        if state["coherence"] < 0.5:
            actions.append("ENERGY_LOW: Consider renewal or checkpoint")
        
        if state["memory"]["episodic"] > 50:
            actions.append("MEMORY_PRUNE: Episodic memory getting large")
        
        if state["lattice"]["nodes"] < 10:
            actions.append("LATTICE_GROWTH: Build more relational nodes")
        
        if deliberation["status"] == "recovered":
            actions.append("RECOVERY_HAPPENED: Review failure pattern")
        
        if not actions:
            actions.append("CONTINUE: System stable, keep observing")
        
        return " | ".join(actions)

    def _visualize_state(self, state: Dict[str, Any], deliberation: Dict[str, Any], action: str) -> None:
        """Print live dashboard."""
        coh = state["coherence"]
        coh_bar = "█" * int(coh * 20) + "░" * (20 - int(coh * 20))
        
        print(f"\n{'═' * 60}")
        print(f"  AUTOPILOT CYCLE #{self.cycle_count:04d}  [{datetime.now().strftime('%H:%M:%S')}]")
        print(f"{'═' * 60}")
        print(f"  Coherence: [{coh_bar}] {coh:.2f}")
        print(f"  Energy:    {state['energy']['remaining']:.1f} / {state['energy']['budget']}")
        print(f"  Files:     {state['project']['py_files']} py | {state['project']['directories']} dirs")
        print(f"  Lattice:   {state['lattice']['nodes']} nodes | {state['lattice']['edges']} edges")
        print(f"  Memory:    {state['memory']['episodic']} episodic | {state['memory']['semantic_db']} semantic")
        print(f"{'─' * 60}")
        print(f"  Deliberation: {deliberation['status']} | decision={deliberation['decision']['decision']}")
        print(f"  Action: {action}")
        print(f"{'═' * 60}")

    def run_cycle(self) -> bool:
        """Run one autopilot cycle. Returns False if should stop."""
        self.cycle_count += 1
        
        # 1. OBSERVE
        state = self._observe()
        state_hash = self._state_hash(state)
        
        # Skip if nothing changed (optimization)
        if state_hash == self.last_state_hash and self.cycle_count > 1:
            print(f"[{self.cycle_count:04d}] No change detected. ", end="\r")
            return True
        
        self.last_state_hash = state_hash
        
        # 2. REMEMBER
        self._store_observation(state)
        
        # 3. DELIBERATE
        deliberation = self._deliberate(state)
        
        # 4. PROPOSE
        action = self._propose_action(state, deliberation)
        
        # 5. VISUALIZE
        self._visualize_state(state, deliberation, action)
        
        # 6. EXECUTE (if needed)
        if "LATTICE_GROWTH" in action:
            self._auto_expand_lattice()
        
        if "MEMORY_PRUNE" in action:
            self._auto_prune_memory()
        
        return True

    def _auto_expand_lattice(self) -> None:
        """Automatically add nodes to lattice based on project structure."""
        files = self.fs.list_dir(".", pattern="*.py")
        for f in files[:5]:
            name = Path(f["path"]).stem
            if not self.kernel.lattice.get_node(name):
                self.kernel.lattice.add_node(
                    name, "file", name,
                    {"type": "python_module", "size": f["size"]}
                )
                self.kernel.lattice.add_edge("project_root", name, "contains")
        print(f"    [AUTO] Expanded lattice: +{min(len(files), 5)} nodes")

    def _auto_prune_memory(self) -> None:
        """Prune old episodic memory entries."""
        count = self.episodic.prune_old(keep=100)
        print(f"    [AUTO] Pruned {count} old episodic entries")

    def run(self, max_cycles: Optional[int] = None) -> None:
        """Run autopilot loop."""
        print("=" * 60)
        print("  NOESIS AUTOPILOT — GAZ W PODŁOGĘ")
        print("=" * 60)
        print(f"  Interval: {self.interval}s | Max cycles: {max_cycles or '∞'}")
        print("  Press Ctrl+C to stop")
        print("=" * 60)
        
        try:
            while True:
                if max_cycles and self.cycle_count >= max_cycles:
                    break
                if not self.run_cycle():
                    break
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print(f"\n\n{'=' * 60}")
            print(f"  AUTOPILOT STOPPED after {self.cycle_count} cycles")
            print(f"  Final coherence: {self._estimate_coherence()}")
            print(f"  Total observations: {self.episodic.count()}")
            print(f"{'=' * 60}")


if __name__ == "__main__":
    kernel = NoesisKernel(init_database=True)
    autopilot = NoesisAutopilot(kernel, interval=3.0)
    autopilot.run(max_cycles=10)
