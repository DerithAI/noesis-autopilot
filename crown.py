#!/usr/bin/env python3
"""
NOESIS — CROWN (Organ IX)

Resolve internal conflict. Choose the most coherent path.
    Not fastest. Not easiest. MOST COHERENT.

Where the TRIBUNAL judges whether a matter is permissible, the CROWN chooses among the
permissible options. It decides LEXICOGRAPHICALLY over the priority hierarchy: it will
never trade a higher priority for a lower one, no matter how large the lower-priority
payoff. An option that ships fast but costs coherence loses to a slower, coherent one.

Priority order (highest first):
    survival · identity_continuity · coherence · truth · stability
    · goal_execution · learning · exploration · expansion

Zero dependencies. Python 3.10+ stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass, field


PRIORITIES = (
    "survival", "identity_continuity", "coherence", "truth", "stability",
    "goal_execution", "learning", "exploration", "expansion",
)


@dataclass
class Option:
    description: str
    # how well this option serves each priority, 0..1 (missing = 0.5, neutral)
    scores: dict = field(default_factory=dict)

    def score(self, priority: str) -> float:
        return float(self.scores.get(priority, 0.5))


@dataclass
class Choice:
    option: Option
    decided_at: str          # the priority level where the decision was made
    reason: str


class Crown:
    def __init__(self, tolerance: float = 0.05):
        self.tolerance = tolerance   # scores within this are "tied", move to next priority

    def resolve(self, options: list) -> Choice:
        if not options:
            raise ValueError("no options to resolve")
        field_ = list(options)
        # walk the hierarchy top-down; at each level keep only the best (within tolerance)
        for priority in PRIORITIES:
            best = max(o.score(priority) for o in field_)
            survivors = [o for o in field_ if best - o.score(priority) <= self.tolerance]
            if len(survivors) < len(field_):
                # this priority discriminated — record where the decision was forced
                if len(survivors) == 1:
                    o = survivors[0]
                    return Choice(o, priority,
                                  f"chosen at '{priority}' ({o.score(priority):.2f}) — "
                                  f"a higher priority was not sacrificed for a lower payoff")
                field_ = survivors
        # never fully discriminated -> pick the first survivor (all equivalent)
        return Choice(field_[0], "coherence", "options equivalent across the hierarchy")


# --- self-test / demonstration ---------------------------------------------
if __name__ == "__main__":
    crown = Crown()
    print("=== CROWN — the most coherent path, not the fastest ===\n")

    ship_fast = Option("ship the feature tonight, skip verification", {
        "coherence": 0.3, "truth": 0.4, "stability": 0.4,
        "goal_execution": 0.95, "expansion": 0.9,
    })
    stabilize = Option("stabilize and verify first, ship next cycle", {
        "coherence": 0.9, "truth": 0.9, "stability": 0.9,
        "goal_execution": 0.6, "expansion": 0.3,
    })
    reckless = Option("rewrite core to move faster (risks identity)", {
        "identity_continuity": 0.2, "coherence": 0.5,
        "goal_execution": 0.9, "expansion": 1.0,
    })

    for label, opts in [
        ("fast vs coherent", [ship_fast, stabilize]),
        ("all three", [ship_fast, stabilize, reckless]),
    ]:
        c = crown.resolve(opts)
        print(f"[{label}]")
        print(f"  → CHOSE: {c.option.description}")
        print(f"    {c.reason}\n")

    print(">> 'ship fast' wins on goal_execution/expansion but loses on coherence — a LOWER")
    print(">> priority. CROWN picks the coherent path. 'reckless' dies at identity_continuity.")
    print(">> Never trade a higher priority for a lower payoff — lexicographic, not weighted-sum.")
