"""
JARVIS — Persistent AI Assistant
Entry point.

Usage:
    python main.py              # Start Jarvis
    python main.py --cycle      # Run one cycle and exit
    python main.py --stats      # Show memory stats
"""
import argparse
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.cycle import JarvisCycle
from core.seed import DEFAULT_SEED
from memory import MemoryStore
from scheduler import Scheduler
from voice import VoiceModule

def main():
    parser = argparse.ArgumentParser(description="JARVIS — Persistent AI Assistant")
    parser.add_argument("--cycle", action="store_true", help="Run one cycle and exit")
    parser.add_argument("--stats", action="store_true", help="Show memory stats")
    parser.add_argument("--input", type=str, help="Input text for cycle")
    parser.add_argument("--voice", action="store_true", help="Enable voice module")
    args = parser.parse_args()
    
    # Initialize components
    memory = MemoryStore()
    voice = VoiceModule() if args.voice else None
    scheduler = Scheduler()
    
    # Create Jarvis instance
    jarvis = JarvisCycle(
        seed=DEFAULT_SEED.copy(),
        memory=memory,
        voice=voice,
        home=None,  # Will be added later
    )
    
    if args.stats:
        stats = memory.get_stats()
        print(json.dumps(stats, indent=2))
        return
    
    if args.cycle:
        print(f"[JARVIS] Running cycle with input: {args.input or 'none'}")
        capsule = jarvis.run_cycle(args.input)
        print(f"[JARVIS] Cycle complete:")
        print(f"  Signal: {capsule['signal']['type']}")
        print(f"  Decision: {capsule['decision']['action']}")
        print(f"  Action: {capsule['action']['output']}")
        print(f"  Check: success={capsule['check']['success']}")
        print(f"  CALM: {capsule['calm']}")
        print(f"  Remembered: {capsule['remembered']}")
        return
    
    # Interactive mode
    print("=" * 50)
    print("  JARVIS v1.0.0 — Persistent AI Assistant")
    print("  Type 'exit' to quit, 'stats' for memory stats")
    print("=" * 50)
    
    # Start scheduler for background tasks
    scheduler.add_task("heartbeat", 60, lambda: print("[JARVIS] Heartbeat"))
    scheduler.start()
    
    try:
        while True:
            user_input = input("\n> ").strip()
            if user_input.lower() in ("exit", "quit", "q"):
                break
            elif user_input.lower() == "stats":
                print(json.dumps(memory.get_stats(), indent=2))
                continue
            elif not user_input:
                continue
            
            capsule = jarvis.run_cycle(user_input)
            print(f"  → {capsule['action']['output']}")
            print(f"  CALM: {capsule['calm']}")
    except KeyboardInterrupt:
        print("\n[JARVIS] Shutting down...")
    finally:
        scheduler.stop()

if __name__ == "__main__":
    main()
