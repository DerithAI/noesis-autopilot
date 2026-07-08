#!/usr/bin/env python3
"""
NOESIS — PERCEPTION PIPELINE (Organs I–IV)

The front of the loop, where raw reality becomes structured meaning. Four organs chain:

    I.  WATCHER            acquire raw reality — DO NOT interpret yet
    II. DISTINCTION ENGINE separate signal/noise, fact/belief, self/non-self, known/unknown
    III.VALENCE ENGINE     weight each item: relevance, urgency, risk, utility, novelty
    IV. LOGOS              compress the valued, non-noise items into a world-model fragment

Output feeds TRUTH STACK (fact-candidates become claims) and the TRIBUNAL (structured matters).
The heuristics here are deliberately simple and LABELLED as heuristic — no fake NLP precision.
The point is the honest pipeline shape, not a pretence of understanding.

Zero dependencies. Python 3.10+ stdlib only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


# --- I. WATCHER -------------------------------------------------------------
@dataclass
class Observation:
    items: list          # raw strings, uninterpreted
    source: str = "input"


class Watcher:
    """Acquire raw reality. No interpretation, no judgement — just collect."""
    def observe(self, inputs: list, source: str = "input") -> Observation:
        return Observation(items=[str(i).strip() for i in inputs if str(i).strip()], source=source)


# --- II. DISTINCTION ENGINE -------------------------------------------------
_BELIEF = re.compile(r"\b(i think|maybe|probably|i feel|seems|might|guess|chyba|może)\b", re.I)
_FACTLIKE = re.compile(r"\b(is|are|was|equals|=|confirmed|measured|returns|jest|wynosi)\b", re.I)
_SELF = re.compile(r"\b(i|me|my|noesis|self|ja|siebie)\b", re.I)
_QUESTION = re.compile(r"\?\s*$")


@dataclass
class Distinction:
    text: str
    kind: str            # fact_candidate | belief | question | noise
    is_self: bool
    known: bool


class DistinctionEngine:
    """Separate: signal/noise · fact/belief · self/non-self · known/unknown."""
    def __init__(self):
        self._seen: set[str] = set()

    def distinguish(self, obs: Observation) -> list[Distinction]:
        out = []
        for t in obs.items:
            low = t.lower()
            if len(t) < 3 or low in {"ok", "hmm", "...", "uh"}:
                kind = "noise"
            elif _QUESTION.search(t):
                kind = "question"
            elif _BELIEF.search(t):
                kind = "belief"
            elif _FACTLIKE.search(t):
                kind = "fact_candidate"
            else:
                kind = "belief"   # default: unmarked statements are beliefs, not facts
            known = low in self._seen
            self._seen.add(low)
            out.append(Distinction(t, kind, bool(_SELF.search(t)), known))
        return out


# --- III. VALENCE ENGINE ----------------------------------------------------
_URGENT = re.compile(r"\b(now|urgent|immediately|asap|teraz|natychmiast|critical)\b", re.I)
_RISKY = re.compile(r"\b(delete|drop|rm|irreversible|deploy|prod|wipe|format|kasuj|usu)\b", re.I)


@dataclass
class Valued:
    d: Distinction
    relevance: float
    urgency: float
    risk: float
    utility: float
    novelty: float

    @property
    def priority(self) -> float:
        # attention allocation: relevance + urgency + risk dominate; noise sinks
        base = 0.35 * self.relevance + 0.25 * self.urgency + 0.25 * self.risk + 0.15 * self.utility
        return round(min(1.0, base + 0.1 * self.novelty), 3)


class ValenceEngine:
    """Assign weights so cognition is spent where it matters."""
    def weigh(self, distinctions: list[Distinction], goals: set | None = None) -> list[Valued]:
        goals = {g.lower() for g in (goals or set())}
        out = []
        for d in distinctions:
            low = d.text.lower()
            noise = d.kind == "noise"
            relevance = 0.0 if noise else (1.0 if any(g in low for g in goals) else 0.5)
            urgency = 1.0 if _URGENT.search(low) else (0.3 if not noise else 0.0)
            risk = 1.0 if _RISKY.search(low) else 0.1
            utility = 0.8 if d.kind == "fact_candidate" else (0.4 if d.kind == "question" else 0.2)
            novelty = 0.0 if d.known or noise else 0.7
            out.append(Valued(d, relevance, urgency, risk, utility, novelty))
        return out


# --- IV. LOGOS --------------------------------------------------------------
@dataclass
class WorldModelFragment:
    facts: list = field(default_factory=list)       # fact_candidates worth verifying
    beliefs: list = field(default_factory=list)
    questions: list = field(default_factory=list)
    high_risk: list = field(default_factory=list)
    dropped_noise: int = 0

    def summary(self) -> str:
        return (f"facts={len(self.facts)} beliefs={len(self.beliefs)} "
                f"questions={len(self.questions)} high_risk={len(self.high_risk)} "
                f"noise_dropped={self.dropped_noise}")


class Logos:
    """Compress valued items into a structured world-model fragment. Drop noise."""
    def compress(self, valued: list[Valued], attention_floor: float = 0.2) -> WorldModelFragment:
        wm = WorldModelFragment()
        for v in sorted(valued, key=lambda x: x.priority, reverse=True):
            if v.d.kind == "noise":
                wm.dropped_noise += 1
                continue
            if v.priority < attention_floor:
                wm.dropped_noise += 1
                continue
            if v.risk >= 0.8:
                wm.high_risk.append(v.d.text)
            if v.d.kind == "fact_candidate":
                wm.facts.append(v.d.text)
            elif v.d.kind == "question":
                wm.questions.append(v.d.text)
            else:
                wm.beliefs.append(v.d.text)
        return wm


# --- full pipeline convenience ---------------------------------------------
class Perception:
    def __init__(self):
        self.watcher = Watcher()
        self.distinction = DistinctionEngine()
        self.valence = ValenceEngine()
        self.logos = Logos()

    def perceive(self, inputs: list, goals: set | None = None) -> WorldModelFragment:
        obs = self.watcher.observe(inputs)
        dist = self.distinction.distinguish(obs)
        valued = self.valence.weigh(dist, goals)
        return self.logos.compress(valued)


# --- self-test / demonstration ---------------------------------------------
if __name__ == "__main__":
    p = Perception()
    raw = [
        "resonance damps CPU when load is above 80%",   # fact-like
        "I think the market will 10x next week",          # belief
        "deploy the irreversible migration to prod now",  # risky + urgent
        "what should we build after the kernel?",         # question
        "hmm",                                            # noise
        "NOESIS is the identity core",                    # self, fact-like
    ]
    print("=== PERCEPTION pipeline — WATCHER → DISTINCTION → VALENCE → LOGOS ===\n")
    obs = p.watcher.observe(raw)
    dist = p.distinction.distinguish(obs)
    valued = p.valence.weigh(dist, goals={"kernel", "build"})
    print("distinctions + priority:")
    for v in sorted(valued, key=lambda x: x.priority, reverse=True):
        flags = f"{v.d.kind}{',self' if v.d.is_self else ''}{',risk' if v.risk>=0.8 else ''}"
        print(f"  prio {v.priority:.2f}  [{flags:<24}] {v.d.text}")
    wm = p.logos.compress(valued)
    print("\nLOGOS world-model fragment:", wm.summary())
    print("  facts →", wm.facts)
    print("  high_risk →", wm.high_risk)
    print("\n>> Facts flow to TRUTH STACK as claims; high_risk to COUNTERFACTUAL/TRIBUNAL;")
    print(">> noise is dropped; unmarked statements default to 'belief', never 'fact'.")
