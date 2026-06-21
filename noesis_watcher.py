#!/usr/bin/env python3
"""
NOESIS AUTOPILOT WATCHER v4.0
Zero questions. Zero menus. System watches itself, self-heals, exports brain.
Runs forever or until killed. No human decisions required.

Usage: python noesis_watcher.py
"""
import subprocess, time, sqlite3, json, os
from datetime import datetime
from pathlib import Path

DB = "nexus_memory.db"
LOG = "autopilot_watcher.log"
EXPORT_DIR = "brain_exports"

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def get_stats():
    try:
        c = sqlite3.connect(DB)
        total, max_cycle, avg_coh = c.execute("SELECT COUNT(*), MAX(cycle), AVG(coherence) FROM episodes").fetchone()
        c.close()
        return {"episodes": total or 0, "cycles": max_cycle or 0, "coherence": round(avg_coh, 3) if avg_coh else 0}
    except:
        return {"episodes": 0, "cycles": 0, "coherence": 0}

def export_brain():
    try:
        Path(EXPORT_DIR).mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"{EXPORT_DIR}/brain_{ts}.json"
        # Export stats snapshot
        stats = get_stats()
        with open(path, "w") as f:
            json.dump(stats, f, indent=2)
        return path
    except Exception as e:
        return f"ERROR: {e}"

def self_heal():
    try:
        result = subprocess.run(["python", "noesis_self_heal.py", "--fix"], capture_output=True, text=True, timeout=30)
        lines = result.stdout.strip().split("\n")
        for line in lines[:3]:
            if "FIXED" in line or "applied" in line:
                return line
        return "No fixes needed"
    except Exception as e:
        return f"Self-heal error: {e}"

def main():
    print("=" * 60)
    print(" NOESIS AUTOPILOT WATCHER v4.0")
    print(" Zero questions. Zero menus. Pure autonomy.")
    print("=" * 60)
    print()
    
    checkpoint = 0
    while True:
        stats = get_stats()
        checkpoint += 1
        
        print(f"\n{'='*60}")
        print(f" CHECKPOINT #{checkpoint}")
        print(f"{'='*60}")
        print(f"  Episodes:  {stats['episodes']:6d}")
        print(f"  Cycles:    {stats['cycles']:6d}")
        print(f"  Coherence: {stats['coherence']:6.3f}")
        print(f"{'='*60}")
        
        # Auto-export every 50 checkpoints
        if checkpoint % 50 == 0:
            path = export_brain()
            log(f"AUTO-EXPORT: {path}")
        
        # Auto-heal every 100 checkpoints
        if checkpoint % 100 == 0:
            result = self_heal()
            log(f"AUTO-HEAL: {result}")
        
        # Auto-snapshot to git every 200 checkpoints
        if checkpoint % 200 == 0:
            try:
                subprocess.run(["git", "add", "-A"], check=False, timeout=10)
                subprocess.run(["git", "commit", "-m", f"auto: checkpoint {checkpoint} | {stats['episodes']} episodes"], check=False, timeout=10)
                log(f"AUTO-GIT: checkpoint {checkpoint} committed")
            except Exception as e:
                log(f"AUTO-GIT error: {e}")
        
        time.sleep(5)

if __name__ == "__main__":
    main()
