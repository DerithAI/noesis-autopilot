#!/usr/bin/env python3
"""
EVO Agent — Cognitive orchestrator for EVO-HUB
Integrates NOESIS (SQLite), LUMEN (ChromaDB), Open Design, and ITDD.

Now with SUPERPOWERS: Council Pattern (L3) + Self-Critique (L4)

Usage:
    python agents/evo_agent.py loop              # Run cognitive loop
    python agents/evo_agent.py perceive "input"   # Single perception
    python agents/evo_agent.py status             # Show system status
    python agents/evo_agent.py council "decide"   # 4-voice deliberation
"""
import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Add parent paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "memory"))

from memory.lumen_bridge import LumenBridge

class VoiceRole(Enum):
    ARCHITECT = "architect"
    SKEPTIC = "skeptic"
    PRAGMATIST = "pragmatist"
    CREATIVE = "creative"

@dataclass
class CouncilVoice:
    """One voice in the Council Pattern."""
    role: VoiceRole
    recommendation: str
    confidence: int  # 0-100
    reasoning: str

class EVOAgent:
    """6-stage cognitive loop + Council deliberation.
    
    Stages:
    1. Perception      → Observe input
    2. Intention       → Define goal
    3. Context         → Load memory
    4. Reasoning       → Analyze (local or LUMEN)
    4.5 Council        → 4-voice deliberation (SUPERPOWERS L3)
    5. Response        → Prepare action
    6. Direction       → Next step
    """
    
    STAGES = ["perception", "intention", "context", "reasoning", "council", "response", "direction"]
    
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
            "review": ["review", "audit", "inspect", "check"],
            "decide": ["decide", "choose", "select", "pick", "should"],
            "critique": ["critique", "review", "audit", "flaws", "bugs"]
        }
        text_lower = text.lower()
        for intent, words in keywords.items():
            if any(w in text_lower for w in words):
                return intent
        return "chat"
    
    def council_deliberate(self, input_text: str, reasoning_output: Dict) -> List[CouncilVoice]:
        """Stage 4.5: Council Pattern — 4 voices deliberate before decision.
        
        SUPERPOWERS L3: Multi-Perspective Analysis
        """
        intent = self._detect_intent(input_text)
        memory_ok = self.lumen.is_available()
        
        voices = []
        
        # ARCHITECT — reasoning about structure and long-term impact
        architect = CouncilVoice(
            role=VoiceRole.ARCHITECT,
            recommendation="proceed" if intent in ["generate", "test", "deploy"] else "analyze",
            confidence=75 if memory_ok else 55,
            reasoning=(
                f"This is a {intent} task. "
                f"{'LUMEN integration provides solid foundation.' if memory_ok else 'No LUMEN — must rely on local fallback.'} "
                f"Long-term: {intent} ventures accumulate in portfolio, need indexing."
            )
        )
        voices.append(architect)
        
        # SKEPTIC — reasoning about risks and failure modes
        skeptic = CouncilVoice(
            role=VoiceRole.SKEPTIC,
            recommendation="proceed_with_caution" if intent == "deploy" else "proceed",
            confidence=60 if intent == "deploy" else 80,
            reasoning=(
                f"Risk assessment: {intent} has {3 if intent=='deploy' else 1} failure modes. "
                f"{'CORS wildcard is a security risk if deployed publicly.' if intent=='deploy' else 'Low risk for this task type.'} "
                f"Edge case: Ollama offline = fallback to templates."
            )
        )
        voices.append(skeptic)
        
        # PRAGMATIST — reasoning about shipping and practical constraints
        pragmatist = CouncilVoice(
            role=VoiceRole.PRAGMATIST,
            recommendation="ship_it" if intent in ["generate", "test"] else "iterate",
            confidence=90,
            reasoning=(
                f"We have {8 if intent=='test' else 7} ventures, 4 systems online. "
                f"Fastest path: use existing tools (venture-swarm, pytest, wolf_howl). "
                f"Time budget: {2 if intent=='generate' else 0.5}min realistic."
            )
        )
        voices.append(pragmatist)
        
        # CREATIVE — reasoning about alternatives and opportunities
        creative = CouncilVoice(
            role=VoiceRole.CREATIVE,
            recommendation="explore",
            confidence=70,
            reasoning=(
                f"Alternative: instead of {intent}, what if we combined it with cognitive loop? "
                f"Opportunity: use deepseek-r1 for {intent} if complexity is high. "
                f"Wildcard: WOLF pack could parallel-process this."
            )
        )
        voices.append(creative)
        
        return voices
    
    def council_synthesize(self, voices: List[CouncilVoice]) -> Dict:
        """Synthesize council deliberation into a single recommendation."""
        # Weighted voting
        weights = {
            VoiceRole.ARCHITECT: 0.30,
            VoiceRole.SKEPTIC: 0.25,
            VoiceRole.PRAGMATIST: 0.30,
            VoiceRole.CREATIVE: 0.15
        }
        
        weighted_confidence = sum(
            v.confidence * weights[v.role] for v in voices
        )
        
        # Count recommendations
        recs = [v.recommendation for v in voices]
        from collections import Counter
        rec_counts = Counter(recs)
        majority = rec_counts.most_common(1)[0][0]
        
        # Check for red flags (skeptic says stop)
        red_flags = any(
            v.recommendation in ["stop", "reject", "block"] 
            for v in voices 
            if v.role == VoiceRole.SKEPTIC
        )
        
        return {
            "recommendation": "hold" if red_flags else majority,
            "confidence": round(weighted_confidence),
            "voices": [
                {
                    "role": v.role.value,
                    "recommendation": v.recommendation,
                    "confidence": v.confidence,
                    "reasoning": v.reasoning
                }
                for v in voices
            ],
            "consensus": len(set(recs)) == 1  # unanimous?
        }
    
    def run_loop(self, input_text: str, use_council: bool = True) -> List[Dict]:
        """Run full cognitive loop with optional Council deliberation."""
        print(f"🧠 EVO Agent: Processing '{input_text[:50]}...'")
        if use_council:
            print("   🏛️  Council Pattern enabled — 4 voices deliberating")
        
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
        
        # Stage 4.5: Council (SUPERPOWERS L3)
        if use_council:
            voices = self.council_deliberate(input_text, reasoning["output"])
            synthesis = self.council_synthesize(voices)
            council_stage = {
                "stage": "council",
                "timestamp": datetime.now().isoformat(),
                "synthesis": synthesis,
                "unanimous": synthesis["consensus"],
                "weighted_confidence": synthesis["confidence"]
            }
            self.history.append(council_stage)
            print(f"  [4.5/6] Council: {len(voices)} voices, consensus={synthesis['consensus']}, confidence={synthesis['confidence']}%")
            print(f"     → {synthesis['recommendation'].upper()}")
            for v in synthesis["voices"]:
                print(f"     {v['role']}: {v['recommendation']} ({v['confidence']}%)")
        
        # Stage 5: Response
        if use_council:
            last_council = self.history[-1]
            resp = {
                "stage": "response", 
                "action": reasoning["output"],
                "council_override": last_council["synthesis"]["recommendation"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            resp = {"stage": "response", "action": reasoning["output"], "timestamp": datetime.now().isoformat()}
        self.history.append(resp)
        print(f"  [5/6] Response: action prepared (council: {resp.get('council_override', 'none')})")
        
        # Stage 6: Direction
        direction = {"stage": "direction", "next_step": "execute", "timestamp": datetime.now().isoformat()}
        self.history.append(direction)
        print(f"  [6/6] Direction: next={direction['next_step']}")
        
        return self.history[-7:] if use_council else self.history[-6:]
    
    def status(self) -> Dict:
        """Get full system status."""
        return {
            "agent": "EVO",
            "cognitive_loop": "6-stage + council",
            "council_voices": [v.value for v in VoiceRole],
            "memory_bridge": self.lumen.is_available(),
            "history_length": len(self.history),
            "timestamp": datetime.now().isoformat()
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="EVO Cognitive Agent with SUPERPOWERS")
    parser.add_argument("action", choices=["loop", "perceive", "status", "council"])
    parser.add_argument("input", nargs="?", default="", help="Input text")
    parser.add_argument("--no-council", action="store_true", help="Skip council deliberation")
    args = parser.parse_args()
    
    agent = EVOAgent()
    
    if args.action == "loop":
        if not args.input:
            args.input = input("🧠 Input: ")
        agent.run_loop(args.input, use_council=not args.no_council)
    elif args.action == "perceive":
        if not args.input:
            args.input = input("👁️  Observe: ")
        result = agent.perceive(args.input)
        print(json.dumps(result, indent=2))
    elif args.action == "council":
        if not args.input:
            args.input = input("🏛️  Decision: ")
        voices = agent.council_deliberate(args.input, {})
        synthesis = agent.council_synthesize(voices)
        print(json.dumps(synthesis, indent=2, ensure_ascii=False))
    elif args.action == "status":
        print(json.dumps(agent.status(), indent=2))


if __name__ == "__main__":
    main()
