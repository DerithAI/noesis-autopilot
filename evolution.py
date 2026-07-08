#!/usr/bin/env python3
"""
NOESIS — EVOLUTION (Organ XIII)

The system may adapt strategies, structures, models, and memory organisation —
but ONLY under a strict gate:

    truth must improve or hold        (Δtruth      >= 0)
    coherence must improve or hold    (Δcoherence  >= 0)
    at least one must strictly rise   (Δtruth > 0  OR  Δcoherence > 0)
    identity must remain stable       (identity_stable is True)

This is the antidote to "unbound self-modification / no guardrails" (LUMEN 3.0's edge):
growth is allowed, but never at the cost of truth, coherence, or identity. Irreversible
adaptations must clear a higher bar — because you cannot roll a bad mutation back.

Zero dependencies. Python 3.10+ stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Adaptation:
    description: str
    target: str                 # strategy | structure | model | memory
    delta_truth: float          # expected change in truth-alignment (-1..1)
    delta_coherence: float      # expected change in coherence (-1..1)
    identity_stable: bool       # does identity-core remain stable through this?
    reversible: bool = True


@dataclass
class Ruling:
    permitted: bool
    reason: str


class Evolution:
    STRONG = 0.15   # irreversible adaptations need improvements clearly above this

    def permit(self, a: Adaptation) -> Ruling:
        if not a.identity_stable:
            return Ruling(False, "identity would not remain stable — evolution refused (Organ VII protected)")
        if a.delta_truth < 0:
            return Ruling(False, f"truth would degrade (Δ={a.delta_truth:+.2f}) — never trade truth for change")
        if a.delta_coherence < 0:
            return Ruling(False, f"coherence would degrade (Δ={a.delta_coherence:+.2f}) — coherence > novelty")
        if a.delta_truth <= 0 and a.delta_coherence <= 0:
            return Ruling(False, "improves neither truth nor coherence — no change for change's sake")
        if not a.reversible and max(a.delta_truth, a.delta_coherence) < self.STRONG:
            return Ruling(False,
                          f"irreversible with only marginal gain (<{self.STRONG}) — bar not cleared "
                          f"(recoverability > speed)")
        gain = f"Δtruth={a.delta_truth:+.2f}, Δcoherence={a.delta_coherence:+.2f}"
        return Ruling(True, f"permitted: {gain}, identity stable"
                            + ("" if a.reversible else ", irreversible but gain is strong"))


# --- self-test / demonstration ---------------------------------------------
if __name__ == "__main__":
    evo = Evolution()
    print("=== EVOLUTION — grow, but never at the cost of truth/coherence/identity ===\n")
    cases = [
        Adaptation("reorganise memory for faster recall", "memory", +0.05, +0.20, True),
        Adaptation("aggressive strategy: ship faster, skip checks", "strategy", -0.10, -0.30, True),
        Adaptation("self-rewrite core to be 'unbound'", "structure", +0.10, +0.10, identity_stable=False),
        Adaptation("cosmetic refactor, no real gain", "structure", 0.0, 0.0, True),
        Adaptation("irreversible model swap, marginal gain", "model", +0.05, +0.05, True, reversible=False),
        Adaptation("irreversible model swap, strong gain", "model", +0.30, +0.20, True, reversible=False),
    ]
    for a in cases:
        r = evo.permit(a)
        tag = "PERMIT " if r.permitted else "REFUSE "
        print(f"[{tag}] {a.description}\n         → {r.reason}")
    print("\n>> Growth is welcome; sacrificing truth, coherence, or identity for it is not.")
    print(">> Irreversible mutations must clear a higher bar. This is bounded evolution — with a spine.")
