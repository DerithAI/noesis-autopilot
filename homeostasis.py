#!/usr/bin/env python3
"""
NOESIS — HOMEOSTASIS (Organ XI)

Core law:  Stabilize before expansion.

FLOOD (Organ XII) reacts to collapse — the level of coherence dropping below the floor.
HOMEOSTASIS is the early-warning sensor: it watches the TREND and the COMPOSITION of the
system's vitals and catches the trajectory drifting toward the edge of the basin *before*
FLOOD ever has to rescue. When vitals degrade, it forbids expansion (priority #9, last)
until the system is stable again.

Monitored vitals (each normalised 0..1, higher = worse):
  * contradiction   — refuted / conflicting claims (read from TRUTH STACK)
  * uncertainty     — how much of the active claim set is unverified (from TRUTH STACK)
  * coherence_loss  — the slope of coherence decline (trend, not level)
  * goal_drift      — churn between the current goal set and the previous one
  * entropy         — jitter/instability of the coherence signal itself

Attractor framing: instability = distance from and speed away from the basin centre.
HOMEOSTASIS sounds the alarm on the way out; FLOOD is the tether that pulls back.

Zero dependencies. Python 3.10+ stdlib only. Optional TRUTH STACK integration.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from enum import Enum
from typing import Optional


WATCH_THRESHOLD = 0.35      # below = stable; expansion allowed
UNSTABLE_THRESHOLD = 0.55   # above = stabilize now, no expansion

# Calibrated 2026-07-08 after the first self-test REFUTED the module's own claim
# (it stayed 'stable' through a clear drift). coherence_loss carries the most weight
# because a falling trend is the earliest true signal of leaving the basin.
WEIGHTS = {
    "coherence_loss": 0.35,
    "contradiction": 0.25,
    "uncertainty": 0.20,
    "goal_drift": 0.15,
    "entropy": 0.05,
}


class Homeostat(str, Enum):
    STABLE = "stable"
    WATCH = "watch"
    UNSTABLE = "unstable"


@dataclass
class Vitals:
    contradiction: float
    uncertainty: float
    coherence_loss: float
    goal_drift: float
    entropy: float

    @property
    def instability(self) -> float:
        return round(sum(getattr(self, k) * w for k, w in WEIGHTS.items()), 3)

    @property
    def verdict(self) -> Homeostat:
        i = self.instability
        if i >= UNSTABLE_THRESHOLD:
            return Homeostat.UNSTABLE
        if i >= WATCH_THRESHOLD:
            return Homeostat.WATCH
        return Homeostat.STABLE

    def as_dict(self) -> dict:
        d = {k: round(getattr(self, k), 3) for k in WEIGHTS}
        d["instability"] = self.instability
        d["verdict"] = self.verdict.value
        return d


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


class Homeostasis:
    def __init__(self, truth_stack=None):
        self.truth_stack = truth_stack
        self._coherence: list[float] = []
        self._prev_goals: Optional[set] = None
        self._last: Optional[Vitals] = None

    # -- signal derivations ---------------------------------------------------
    def _coherence_loss(self) -> float:
        """Net decline across the recent window (peak-to-latest). A drop of ~0.20
        over the window is a full alarm. 0 if flat/improving."""
        w = self._coherence[-5:]
        if len(w) < 2:
            return 0.0
        decline = max(w) - w[-1]          # how far below the recent peak we are
        return _clamp(decline / 0.20)

    def _entropy(self) -> float:
        """Jitter of the coherence signal — an unsteady signal is itself a warning."""
        w = self._coherence[-6:]
        if len(w) < 2:
            return 0.0
        return _clamp(statistics.pstdev(w) / 0.25)

    def _goal_drift(self, goals: Optional[set]) -> float:
        if goals is None:
            return 0.0
        goals = set(goals)
        if self._prev_goals is None:
            self._prev_goals = goals
            return 0.0
        union = self._prev_goals | goals
        drift = 0.0 if not union else 1.0 - len(self._prev_goals & goals) / len(union)
        self._prev_goals = goals
        return _clamp(drift)

    def _from_truth_stack(self) -> tuple[float, float]:
        """(contradiction, uncertainty) computed from the TRUTH STACK, if attached."""
        if self.truth_stack is None:
            return 0.0, 0.0
        claims = self.truth_stack.claims()
        if not claims:
            return 0.0, 0.0
        refuted = sum(1 for c in claims if c.verification_state == "refuted")
        contradiction = refuted / len(claims)
        uncertainty = statistics.fmean(1.0 - c.confidence for c in claims
                                       if c.verification_state != "verified") \
            if any(c.verification_state != "verified" for c in claims) else 0.0
        return _clamp(contradiction), _clamp(uncertainty)

    # -- the reading ----------------------------------------------------------
    def sense(
        self,
        coherence: float,
        goals: Optional[set] = None,
        contradiction: Optional[float] = None,
        uncertainty: Optional[float] = None,
    ) -> Vitals:
        self._coherence.append(_clamp(coherence))
        self._coherence = self._coherence[-32:]

        ts_contradiction, ts_uncertainty = self._from_truth_stack()
        v = Vitals(
            contradiction=_clamp(contradiction if contradiction is not None else ts_contradiction),
            uncertainty=_clamp(uncertainty if uncertainty is not None else ts_uncertainty),
            coherence_loss=self._coherence_loss(),
            goal_drift=self._goal_drift(goals),
            entropy=self._entropy(),
        )
        self._last = v
        return v

    def status(self) -> Homeostat:
        return self._last.verdict if self._last else Homeostat.STABLE

    def may_expand(self) -> bool:
        """Core law: expansion (priority #9) is forbidden unless the system is STABLE."""
        return self.status() == Homeostat.STABLE

    def recommendation(self) -> str:
        s = self.status()
        if s == Homeostat.UNSTABLE:
            return "STABILIZE NOW — freeze expansion; if coherence keeps falling, FLOOD will engage"
        if s == Homeostat.WATCH:
            return "HOLD — no new expansion; reduce uncertainty (verify claims) and recheck"
        return "OK — stable inside the basin; expansion permitted"


# --- self-test / demonstration ---------------------------------------------
if __name__ == "__main__":
    # Cross-organ demo: HOMEOSTASIS reads uncertainty/contradiction from a live TRUTH STACK
    try:
        from truth_stack import TruthStack
        ts = TruthStack(":memory:")
        # mostly unverified claims -> high uncertainty; one refuted -> contradiction
        a = ts.assert_claim("resonance damps CPU", 0.95); ts.verify(a, True)
        ts.assert_claim("system is 95% conscious", 0.2)
        ts.assert_claim("identity is an attractor", 0.85)
        r = ts.assert_claim("memory never decays", 0.6); ts.verify(r, False)
    except Exception:
        ts = None

    h = Homeostasis(truth_stack=ts)
    print("=== HOMEOSTASIS demo — 'stabilize before expansion' ===\n")

    print("-- healthy climb (stable, expansion allowed) --")
    for coh, goals in [(0.70, {"build"}), (0.74, {"build"}), (0.76, {"build", "verify"})]:
        v = h.sense(coh, goals=goals)
        print(f"coh={coh:.2f} instab={v.instability:.2f} [{v.verdict.value:<8}] may_expand={h.may_expand()}")

    print("\n-- drift begins: coherence slips + goals churn + unverified claims pile up --")
    for coh, goals in [(0.66, {"build", "launch"}), (0.58, {"launch", "market", "scale"}), (0.49, {"scale", "expand"})]:
        v = h.sense(coh, goals=goals)
        print(f"coh={coh:.2f} instab={v.instability:.2f} [{v.verdict.value:<8}] may_expand={h.may_expand()}")
        print(f"     vitals: {v.as_dict()}")

    print("\nrecommendation:", h.recommendation())
    print("\n>> Early warning: HOMEOSTASIS should raise WATCH/UNSTABLE while coherence is still")
    print(">> ABOVE FLOOD's 0.30 collapse floor — catching the drift before rescue is needed.")
    if ts:
        ts.close()
