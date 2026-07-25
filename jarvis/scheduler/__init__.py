"""
JARVIS Scheduler — Proactive scheduling, background tasks.
"""
import time
import threading
from typing import Callable, Dict, List
from datetime import datetime, timedelta

class Scheduler:
    """Proactive task scheduler for Jarvis."""
    
    def __init__(self):
        self.tasks: List[Dict] = []
        self.running = False
        self._thread = None
    
    def add_task(self, name: str, interval: int, callback: Callable, args: tuple = ()):
        """Add a recurring task."""
        self.tasks.append({
            "name": name,
            "interval": interval,  # seconds
            "callback": callback,
            "args": args,
            "last_run": None,
            "enabled": True,
        })
    
    def start(self):
        """Start scheduler in background thread."""
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop scheduler."""
        self.running = False
        if self._thread:
            self._thread.join()
    
    def _run(self):
        """Main scheduler loop."""
        while self.running:
            now = time.time()
            for task in self.tasks:
                if not task["enabled"]:
                    continue
                if task["last_run"] is None or (now - task["last_run"]) >= task["interval"]:
                    try:
                        task["callback"](*task["args"])
                        task["last_run"] = now
                    except Exception as e:
                        print(f"[Scheduler] Task {task['name']} failed: {e}")
            time.sleep(1)
