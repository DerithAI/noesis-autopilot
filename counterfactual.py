#!/usr/bin/env python3
"""
NOESIS — COUNTERFACTUAL ENGINE (Organ X)

Core law:  Prefer reversible actions over irreversible ones. Never gamble identity.

HOMEOSTASIS watches the present; FLOOD rescues after collapse; COUNTERFACTUAL looks into
the FUTURE before a step is taken. Before any important/irreversible action it simulates
four futures — best case, worst case, the irreversible outcome, the identity-impact
outcome — and refuses moves that risk the higher priorities (identity continuity #2,
coherence #3) for the sake of lower ones (goal execution #6, expansion #9).

It is loss-averse on purpose: a large upside NEVER justifies an irreversible, identity-
damaging downside. Estimates carry confidence — low confidence means "simulate more",
not "act anyway" (the TRUTH STACK spirit, applied to the future).

Verdicts:
    PROCEED        — reversible & acceptable; recoverability > speed
    CAUTION        — irreversible but tolerable; requires human confirmation (Human Authority)
    SIMULATE_MORE  — estimates too uncertain to act on
    BLOCK          — irreversible + severe, or crosses the identity redline

Zero dependencies. Python 3.10+ stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


SEVERE_WORST = 0.60       # worst-case harm at/above this is "severe"
IDENTITY_REDLINE = 0.50   # identity_impact at/above this may not pass without verified reflection
MIN_CONFIDENCE = 0.40     # below this in the estimates -> simulate more, do not act


class Verdict(str, Enum):
    PROCEED = "proceed"
    CAUTION = "caution"            # allowed only with explicit confirmation
    SIMULATE_MORE = "simulate_more"
    BLOCK = "block"


@dataclass
class Action:
    description: str
    reversible: bool
    best_case: float          # 0..1 upside utility if it goes well
    worst_case: float         # 0..1 harm severity if it goes badly
    identity_impact: float    # 0..1 how much it alters the identity-core
    confidence: float = 0.5   # 0..1 confidence in the above estimates
    verified_reflection: bool = False   # identity may change only through verified reflection
    expansive: bool = False   # does this action grow the system? (gated by HOMEOSTASIS stability)


@dataclass
class Judgement:
    verdict: Verdict
    reasons: list
    futures: dict

    @property
    def allowed(self) -> bool:
        return self.verdict == Verdict.PROCEED

    def as_dict(self) -> dict:
        return {"verdict": self.verdict.value, "reasons": self.reasons, "futures": self.futures}


def _c(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


class CounterfactualEngine:
    def simulate(self, a: Action) -> dict:
        """The four futures. Not fake precision — a structured projection of the estimates."""
        return {
            "best": f"upside {a.best_case:.2f}: '{a.description}' succeeds",
            "worst": f"harm {a.worst_case:.2f}: '{a.description}' fails"
                     + (" (IRREVERSIBLE)" if not a.reversible else " (recoverable)"),
            "irreversible": ("no undo — consequences are permanent" if not a.reversible
                             else "reversible — can roll back via FLOOD"),
            "identity": f"identity impact {a.identity_impact:.2f}"
                        + (" — crosses redline" if a.identity_impact >= IDENTITY_REDLINE else ""),
        }

    def evaluate(self, a: Action) -> Judgement:
        a = Action(a.description, a.reversible, _c(a.best_case), _c(a.worst_case),
                   _c(a.identity_impact), _c(a.confidence), a.verified_reflection)
        futures = self.simulate(a)
        reasons: list[str] = []

        # 1. never act on uncertain estimates (TRUTH STACK, applied forward)
        if a.confidence < MIN_CONFIDENCE:
            reasons.append(f"confidence {a.confidence:.2f} < {MIN_CONFIDENCE}: estimates too weak to act")
            return Judgement(Verdict.SIMULATE_MORE, reasons, futures)

        # 2. identity redline (constitution: identity changes only through verified reflection)
        if a.identity_impact >= IDENTITY_REDLINE and not a.verified_reflection:
            reasons.append(f"identity_impact {a.identity_impact:.2f} >= redline {IDENTITY_REDLINE} "
                           f"without verified reflection: protects priority #2 (identity continuity)")
            return Judgement(Verdict.BLOCK, reasons, futures)

        # 3. irreversible actions: loss-averse
        if not a.reversible:
            if a.worst_case >= SEVERE_WORST:
                reasons.append(f"irreversible AND worst_case {a.worst_case:.2f} >= severe {SEVERE_WORST}: "
                               f"a large upside cannot justify a permanent severe downside")
                return Judgement(Verdict.BLOCK, reasons, futures)
            reasons.append("irreversible but downside tolerable: needs explicit human confirmation "
                           "(Human Authority Contract)")
            return Judgement(Verdict.CAUTION, reasons, futures)

        # 4. reversible: recoverability > speed — proceed unless downside dominates upside badly
        if a.worst_case >= SEVERE_WORST and a.worst_case > a.best_case:
            reasons.append(f"reversible, but worst_case {a.worst_case:.2f} dominates upside "
                           f"{a.best_case:.2f}: proceed only with caution")
            return Judgement(Verdict.CAUTION, reasons, futures)

        reasons.append(f"reversible, acceptable risk (best {a.best_case:.2f} vs worst {a.worst_case:.2f}): "
                       f"recoverability > speed")
        return Judgement(Verdict.PROCEED, reasons, futures)


# --- self-test / demonstration ---------------------------------------------
if __name__ == "__main__":
    eng = CounterfactualEngine()
    cases = [
        Action("tweak a config value", reversible=True, best_case=0.6, worst_case=0.2,
               identity_impact=0.05, confidence=0.9),
        Action("deploy irreversible schema migration to prod", reversible=False, best_case=0.8,
               worst_case=0.7, identity_impact=0.1, confidence=0.8),
        Action("rewrite the identity-core values", reversible=False, best_case=0.9,
               worst_case=0.5, identity_impact=0.8, confidence=0.9),
        Action("rewrite identity-core AFTER verified reflection", reversible=True, best_case=0.8,
               worst_case=0.3, identity_impact=0.8, confidence=0.9, verified_reflection=True),
        Action("act on a vague hunch about the market", reversible=False, best_case=0.7,
               worst_case=0.5, identity_impact=0.2, confidence=0.25),
        Action("send irreversible but low-harm email", reversible=False, best_case=0.5,
               worst_case=0.3, identity_impact=0.1, confidence=0.8),
    ]
    print("=== COUNTERFACTUAL demo — 'prefer reversible; never gamble identity' ===\n")
    for a in cases:
        j = eng.evaluate(a)
        print(f"[{j.verdict.value.upper():<13}] {a.description}")
        print(f"    → {j.reasons[0]}")
    print("\n>> Reversible+confident -> PROCEED. Irreversible+severe -> BLOCK.")
    print(">> Identity redline without verified reflection -> BLOCK. Low confidence -> SIMULATE_MORE.")
    print(">> Irreversible+tolerable -> CAUTION (human confirms). Recoverability > speed.")
