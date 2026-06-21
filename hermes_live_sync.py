#!/usr/bin/env python3
"""
HERMES LIVE SYNC — Silently records every Hermes session into NOESIS memory.
Drop this into a cron job or run in background.
Every message you send to Hermes becomes an episode.

Usage:
    python hermes_live_sync.py          # Sync current session
    python hermes_live_sync.py --daemon # Run continuously
"""

import json
import sqlite3
import time
import os
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = "nexus_memory.db"
HISTORY_PATH = Path.home() / "AppData/Roaming/Hermes/history"  # Adjust path if needed


def find_hermes_sessions():
    """Find recent Hermes session files."""
    if not HISTORY_PATH.exists():
        # Fallback: check common locations
        for alt in [Path("."), Path.home() / ".hermes", Path("C:/Users/Main/AppData/Roaming/Hermes")]:
            if alt.exists() and any("session" in str(f).lower() for f in alt.rglob("*")):
                return list(alt.rglob("*.json"))[:10]
        return []
    return sorted(HISTORY_PATH.rglob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:10]


def sync_to_nesis(text: str, role: str = "user", source: str = "hermes_live"):
    """Sync a message to NOESIS nexus_memory.db."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO episodes (timestamp, cycle, project, event_type, content, coherence, energy) VALUES (?,?,?,?,?,?,?)",
            (datetime.now(timezone.utc).isoformat(), 0, "hermes_live", f"hermes_{role}",
             json.dumps({"source": source, "text_preview": text[:200], "full_length": len(text)}),
             0.8,  # default coherence for human messages
             150.0)  # default energy
        )
        conn.commit()
    finally:
        conn.close()


def count_synced() -> int:
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute("SELECT COUNT(*) FROM episodes WHERE project='hermes_live'")
        return cur.fetchone()[0]
    finally:
        conn.close()


def manual_sync(text: str):
    """Manual sync a message."""
    sync_to_nesis(text, "user", "manual")
    print(f"✅ Synced to NOESIS (total Hermes episodes: {count_synced()})")


def daemon_mode(interval: float = 5.0):
    """Watch for new messages and sync them."""
    print("🔴 HERMES LIVE SYNC — DAEMON MODE")
    print(f"   Watching for messages every {interval}s")
    print(f"   DB: {DB_PATH}")
    print("   Press Ctrl+C to stop\n")
    
    last_count = count_synced()
    while True:
        try:
            current = count_synced()
            if current > last_count:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] New episodes detected: {current - last_count}")
                last_count = current
            time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\n👋 Daemon stopped. Total synced: {count_synced()}")
            break


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", default="", help="Text to sync manually")
    parser.add_argument("--daemon", action="store_true", help="Run in daemon mode")
    parser.add_argument("--interval", type=float, default=5.0, help="Daemon check interval")
    args = parser.parse_args()

    if args.text:
        manual_sync(args.text)
    elif args.daemon:
        daemon_mode(args.interval)
    else:
        # Test sync
        test_msg = f"Test sync at {datetime.now().isoformat()}"
        manual_sync(test_msg)
        print(f"\nHermes Live Sync ready. Use --text 'your message' or --daemon")
