#!/usr/bin/env python3
"""
NOESIS — COHERENCE METER (Organ XIV)

Core law:  Coherence is measured, never declared.

Until now every cycle received coherence as an input — a number someone made up.
A self-model fed fiction will FLOOD on noise or never FLOOD at all. This organ
computes coherence from what the body can actually observe about itself:

  * contradiction  — how much of what the system asserted was later REFUTED
  * verification   — how much of what the system believes it has actually verified
  * identity       — does the identity signature hold from cycle to cycle
  * goal stability — are goals continuous, or thrashing every cycle

Each component is 0..1 and auditable (the report says WHY the number is what it is).
An explicit coherence value may still be injected (tests, simulation) — but the
kernel's default is the measured value.

Zero dependencies. Python 3.10+ stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass, field


WEIGHTS = {
    "contradiction": 0.35,   # refuted claims are the loudest incoherence signal
    "verification": 0.25,    # believing much, verifying little = fragile
    "identity": 0.25,        # signature drift = the attractor point itself moved
    "goal_stability": 0.15,  # goal thrash = no continuous line of intent
}

# with an empty truth stack there is nothing to verify yet — agnostic prior,
# inside the seed basin (>= 0.55) so a fresh boot can checkpoint its first seed
EMPTY_STACK_VERIFICATION = 0.6


@dataclass
class CoherenceReport:
    coherence: float
    components: dict = field(default_factory=dict)
    detail: dict = field(default_factory=dict)

    def explain(self) -> str:
        parts = ", ".join(f"{k}={v:.2f}" for k, v in self.components.items())
        return f"coherence={self.coherence:.2f} [{parts}]"


class CoherenceMeter:
    def __init__(self):
        self._prev_signature: str | None = None
        self._prev_goals: set | None = None

    def measure(self, truth, identity, goals: set | None = None) -> CoherenceReport:
        """Compute coherence from observable state. Stateful across cycles:
        remembers the previous identity signature and goal set to detect drift."""
        claims = truth.claims()
        total = len(claims)
        refuted = sum(1 for c in claims if c.verification_state == "refuted")
        facts = sum(1 for c in claims if c.is_fact)

        # 1. contradiction: refutations compound — each one is evidence that the
        #    GENERATOR of claims is unreliable, so trust degrades superlinearly
        contradiction = (1.0 - (refuted / total)) ** 2 if total else 1.0

        # 2. verification: fraction of ALL asserted claims that earned FACT status
        #    (a refuted claim is not "gone" — it is belief mass that failed)
        verification = (facts / total) if total else EMPTY_STACK_VERIFICATION

        # 3. identity continuity: signature must hold cycle to cycle
        sig = identity.signature()
        identity_hold = 1.0 if self._prev_signature in (None, sig) else 0.0
        self._prev_signature = sig

        # 4. goal stability: Jaccard overlap with previous cycle's goals
        goals = set(goals or ())
        if self._prev_goals is None or not (goals | self._prev_goals):
            goal_stability = 1.0
        else:
            goal_stability = len(goals & self._prev_goals) / len(goals | self._prev_goals)
        self._prev_goals = goals

        components = {
            "contradiction": contradiction,
            "verification": verification,
            "identity": identity_hold,
            "goal_stability": goal_stability,
        }
        coherence = sum(WEIGHTS[k] * v for k, v in components.items())
        return CoherenceReport(
            coherence=round(coherence, 4),
            components=components,
            detail={"claims": total, "facts": facts, "refuted": refuted,
                    "signature": sig, "goals": sorted(goals)},
        )


# --- self-test / demonstration ---------------------------------------------
if __name__ == "__main__":
    from truth_stack import TruthStack
    from identity_core import IdentityCore

    truth = TruthStack(":memory:")
    identity = IdentityCore(name="NOESIS", origin="demo", values=["truth"], constraints=[])
    meter = CoherenceMeter()

    print("=== COHERENCE METER demo — measured, never declared ===\n")

    r = meter.measure(truth, identity, {"build"})
    print("fresh boot          ->", r.explain())

    cid = truth.assert_claim("append-only ledger is tamper-evident", 0.95)
    truth.verify(cid, True)
    r = meter.measure(truth, identity, {"build"})
    print("one verified fact   ->", r.explain())

    for i in range(3):
        cid = truth.assert_claim(f"hallucinated metric #{i}", 0.9)
        truth.verify(cid, False)
    r = meter.measure(truth, identity, {"scale", "pivot", "rewrite"})
    print("3 refuted + thrash  ->", r.explain())

    truth.close()
