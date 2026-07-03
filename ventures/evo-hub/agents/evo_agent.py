#!/usr/bin/env python3
"""
EVO Agent — Cognitive orchestrator for EVO-HUB
Integrates NOESIS (SQLite), LUMEN (ChromaDB), Open Design, and ITDD.

Usage:
    python agents/evo_agent.py loop              # Run cognitive loop
    python agents/evo_agent.py perceive "input"   # Single perception
    python agents/evo_agent.py status             # Show system status
"""
import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Add parent paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "memory"))

from memory.lumen_bridge import LumenBridge

class EVOAgent:
    """6-stage cognitive loop: Perception → Intention → Context → Reasoning → Response → Direction"""
    
    STAGES = ["perception", "intention", "context", "reasoning", "response", "direction"]
    
    def __init__(self):
        self.lumen = LumenBridge()
        self.history = []
    
    def perceive(self, input_text: str) -> Dict:
        """Stage 1: Perception — observe input signals."""
        stage = {
            "stage": "perception",
            "timestamp": datetime.now().isoformat(),
            "input": input_text,
            "signals": {
                "length": len(input_text),
                "intent_hint": self._detect_intent(input_text),
                "urgency": "high" if "urgent" in input_text.lower() else "normal"
            }
        }
        self.history.append(stage)
        return stage
    
    def _detect_intent(self, text: str) -> str:
        """Keyword-based intent detection (like LUMEN)."""
        keywords = {
            "generate": ["generate", "create", "build", "make"],
            "test": ["test", "check", "verify", "validate"],
            "deploy": ["deploy", "ship", "publish", "release"],
            "research": ["research", "find", "search", "discover"],
            "review": ["review", "audit", "inspect", "check"]
        }
        text_lower = text.lower()
        for intent, words in keywords.items():
            if any(w in text_lower for w in words):
                return intent
        return "chat"
    
    def run_loop(self, input_text: str) -> List[Dict]:
        """Run full 6-stage cognitive loop."""
        print(f"🧠 EVO Agent: Processing '{input_text[:50]}...'")
        
        # Stage 1: Perception
        p = self.perceive(input_text)
        print(f"  [1/6] Perception: intent={p['signals']['intent_hint']}, urgency={p['signals']['urgency']}")
        
        # Stage 2: Intention
        i = {"stage": "intention", "goal": f"{p['signals']['intent_hint']} something", "timestamp": datetime.now().isoformat()}
        self.history.append(i)
        print(f"  [2/6] Intention: goal={i['goal']}")
        
        # Stage 3: Context
        ctx = {"stage": "context", "memory_available": self.lumen.is_available(), "timestamp": datetime.now().isoformat()}
        self.history.append(ctx)
        print(f"  [3/6] Context: memory={ctx['memory_available']}")
        
        # Stage 4: Reasoning
        if self.lumen.is_available():
            lumen_result = self.lumen.cognitive_loop(input_text)
            reasoning = {"stage": "reasoning", "source": "lumen", "output": lumen_result, "timestamp": datetime.now().isoformat()}
        else:
            reasoning = {"stage": "reasoning", "source": "local", "output": {"suggestion": f"Use {p['signals']['intent_hint']} workflow"}, "timestamp": datetime.now().isoformat()}
        self.history.append(reasoning)
        print(f"  [4/6] Reasoning: source={reasoning['source']}")
        
        # Stage 5: Response
        resp = {"stage": "response", "action": reasoning["output"], "timestamp": datetime.now().isoformat()}
        self.history.append(resp)
        print(f"  [5/6] Response: action prepared")
        
        # Stage 6: Direction
        direction = {"stage": "direction", "next_step": "execute", "timestamp": datetime.now().isoformat()}
        self.history.append(direction)
        print(f"  [6/6] Direction: next={direction['next_step']}")
        
        return self.history[-6:]
    
    def status(self) -> Dict:
        """Get full system status."""
        return {
            "agent": "EVO",
            "cognitive_loop": "6-stage",
            "memory_bridge": self.lumen.is_available(),
            "history_length": len(self.history),
            "timestamp": datetime.now().isoformat()
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="EVO Cognitive Agent")
    parser.add_argument("action", choices=["loop", "perceive", "status"])
    parser.add_argument("input", nargs="?", default="", help="Input text for loop/perceive")
    args = parser.parse_args()
    
    agent = EVOAgent()
    
    if args.action == "loop":
        if not args.input:
            args.input = input("🧠 Input: ")
        agent.run_loop(args.input)
    elif args.action == "perceive":
        if not args.input:
            args.input = input("👁️  Observe: ")
        result = agent.perceive(args.input)
        print(json.dumps(result, indent=2))
    elif args.action == "status":
        print(json.dumps(agent.status(), indent=2))


if __name__ == "__main__":
    main()
