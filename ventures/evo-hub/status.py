#!/usr/bin/env python3
"""
EVO-HUB Status — one-shot observability for the living stack.

Usage:
    python status.py                 # full status
    python status.py --json          # machine-readable
    python status.py --watch 5       # refresh every 5s

Checks:
    :8002 LUMEN OS (m-ai-self)       health + agents + memory
    :8003 EVO-HUB backend            health + lumen_connected
    :5173 frontend (Vite)            dev server + proxy
    Ollama :11434                    local LLM provider
"""
import argparse
import json
import sys
import time
from datetime import datetime

import requests

CHECKS = {
    "lumen": {"url": "http://127.0.0.1:8002", "label": "LUMEN OS :8002"},
    "evo_hub": {"url": "http://127.0.0.1:8003", "label": "EVO-HUB :8003"},
    "frontend": {"url": "http://127.0.0.1:5173", "label": "Frontend :5173"},
    "ollama": {"url": "http://127.0.0.1:11434", "label": "Ollama :11434"},
}


def probe(base: str, path: str = "", timeout: float = 8.0):
    try:
        r = requests.get(base + path, timeout=timeout)
        if r.status_code != 200:
            return {"ok": False, "status": r.status_code, "body": r.text[:120]}
        try:
            return {"ok": True, "status": 200, "data": r.json()}
        except Exception:
            return {"ok": True, "status": 200, "text": r.text[:120]}
    except Exception as e:
        return {"ok": False, "error": str(e)[:120]}


def collect() -> dict:
    out = {"timestamp": datetime.now().isoformat(timespec="seconds")}
    out["lumen"] = probe(CHECKS["lumen"]["url"], "/api/status")
    out["evo_hub"] = probe(CHECKS["evo_hub"]["url"], "/health")
    out["frontend"] = probe(CHECKS["frontend"]["url"], "/health")
    out["ollama"] = probe(CHECKS["ollama"]["url"], "/api/tags")
    return out


def render(s: dict) -> str:
    L = []
    L.append(f"EVO-HUB STATUS  [{s['timestamp']}]")
    L.append("=" * 46)

    l = s["lumen"]
    if l["ok"]:
        d = l["data"]
        mem = d.get("memory", {})
        agents = ", ".join(d.get("agents", []))
        L.append(f"LUMEN OS      UP   {d.get('system')} {d.get('version')}")
        L.append(f"  llm: {d.get('llm')}")
        L.append(f"  agents: {agents}")
        L.append(f"  memory: episodic={mem.get('episodic')} semantic={mem.get('semantic')} ckpt={mem.get('checkpoints')}")
    else:
        L.append(f"LUMEN OS      DOWN {l.get('error') or l.get('status')}")

    e = s["evo_hub"]
    if e["ok"]:
        d = e["data"]
        L.append(f"EVO-HUB       UP   {d.get('status')} | lumen_connected={d.get('lumen_connected')} | v{d.get('version')}")
    else:
        L.append(f"EVO-HUB       DOWN {e.get('error') or e.get('status')}")

    f = s["frontend"]
    if f["ok"]:
        d = f.get("data") or {}
        L.append(f"Frontend      UP   proxy->backend {d.get('status', 'ok')} | lumen={d.get('lumen_connected')}")
    else:
        L.append(f"Frontend      DOWN {f.get('error') or f.get('status')}")

    o = s["ollama"]
    if o["ok"]:
        models = [m.get("name") for m in o["data"].get("models", [])]
        L.append(f"Ollama        UP   models: {', '.join(models[:3]) or 'none'}")
    else:
        L.append(f"Ollama        DOWN {o.get('error') or o.get('status')}")

    L.append("=" * 46)
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="EVO-HUB living stack status")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--watch", type=int, default=0, help="refresh every N seconds")
    args = ap.parse_args()

    if args.json:
        print(json.dumps(collect(), indent=2))
        return

    if args.watch:
        try:
            while True:
                print(render(collect()))
                time.sleep(args.watch)
        except KeyboardInterrupt:
            print("\nbye.")
        return

    print(render(collect()))


if __name__ == "__main__":
    main()
