#!/usr/bin/env python3
"""
WOLF_AI Bridge for EVO-FORGE Bot
Lightweight connector to WOLF_AI pack from forge-bot.
"""
import sys
import json
import argparse
from pathlib import Path

# Add WOLF_AI to path
WOLF_ROOT = Path("C:/Users/Main/WOLF_AI")
if WOLF_ROOT.exists():
    sys.path.insert(0, str(WOLF_ROOT))


def wolf_status():
    """Get WOLF_AI pack status."""
    try:
        from core.wolf import Wolf
        # Create a probe wolf
        probe = Wolf(name="EVO-Probe", role="scout", model="qwen2.5:7b")
        probe.awaken()
        status = {
            "connected": True,
            "wolf": probe.name,
            "role": probe.role,
            "status": probe.status,
            "awakened_at": probe.awakened_at,
            "pack_root": str(WOLF_ROOT)
        }
        print(json.dumps(status, indent=2, ensure_ascii=False))
        return 0
    except Exception as e:
        print(json.dumps({"connected": False, "error": str(e)}, indent=2))
        return 1


def wolf_howl(message: str, frequency: str = "medium"):
    """Send a howl to the WOLF_AI pack."""
    try:
        from core.wolf import Wolf
        wolf = Wolf(name="EVO-Bot", role="messenger", model="qwen2.5:7b")
        wolf.awaken()
        result = wolf.howl(message, frequency)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        return 1


def wolf_hunt(target: str):
    """Initiate a hunt via WOLF_AI."""
    try:
        from core.wolf import Wolf
        wolf = Wolf(name="EVO-Hunter", role="hunter", model="qwen2.5:7b")
        wolf.awaken()
        # Simulate hunt
        result = {
            "hunter": wolf.name,
            "target": target,
            "status": "hunting",
            "message": f"🐺 Pack hunting '{target}'...",
            "timestamp": wolf.awakened_at
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        return 1


def main():
    parser = argparse.ArgumentParser(description="WOLF_AI Bridge for EVO-FORGE")
    sub = parser.add_subparsers(dest="cmd")
    
    sub.add_parser("status", help="Check WOLF_AI status")
    
    howl_cmd = sub.add_parser("howl", help="Send howl to pack")
    howl_cmd.add_argument("message", nargs="+", help="Howl message")
    howl_cmd.add_argument("--freq", default="medium", choices=["low", "medium", "high", "AUUUU"])
    
    hunt_cmd = sub.add_parser("hunt", help="Initiate hunt")
    hunt_cmd.add_argument("target", help="Hunt target")
    
    args = parser.parse_args()
    
    if args.cmd == "status":
        return wolf_status()
    elif args.cmd == "howl":
        return wolf_howl(" ".join(args.message), args.freq)
    elif args.cmd == "hunt":
        return wolf_hunt(args.target)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
