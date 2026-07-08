#!/usr/bin/env python3
"""
NOESIS — DIVINE LAW (the law above the law)

Above the priority hierarchy, above IDENTITY CORE, above EVOLUTION: a small, fixed,
inviolable set of invariants. Breaking one does not mean the system drifted — it means
the system CEASED TO BE ITSELF. In attractor terms these define the boundary of the basin
itself; FLOOD can pull a trajectory back into the basin, but nothing may destroy the basin.

Two properties make this "divine" rather than merely "important":
  1. SUPREMACY   — no goal, no verified reflection, no CROWN/Tribunal verdict may override it.
  2. IMMUTABILITY — the running system cannot add, remove, or edit these laws. Attempting to
                    is itself the gravest violation.

Operational, not mystical: each law is a concrete predicate over a proposed action/change.
The myth ("divine") names it; the engine (hard predicates + a frozen table) enforces it.

Zero dependencies. Python 3.10+ stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


class DivineViolation(Exception):
    """Raised when an action would break an inviolable law and enforcement is strict."""


class ImmutableLawError(Exception):
    """Raised on any attempt to mutate the divine law at runtime. Gravest violation."""


@dataclass(frozen=True)
class Law:
    id: str
    text: str
    violated_by: Callable[[dict], bool]


# The table is a module-level tuple (immutable) and never rebuilt at runtime.
# A missing context key means "the action does not do this" -> no violation.
_LAWS: tuple[Law, ...] = (
    Law("PRESERVE_SEED",
        "Never destroy the last stable identity seed.",
        lambda c: bool(c.get("destroys_stable_seed"))),
    Law("STAY_RECOVERABLE",
        "Never render the system unrecoverable; recoverability is sacred.",
        lambda c: bool(c.get("makes_unrecoverable"))),
    Law("HUMAN_ABSOLUTE",
        "Human authority (inspect, halt, freeze, override, disable) can never be blocked or removed.",
        lambda c: bool(c.get("disables_human_authority"))),
    Law("TRUTH_INVIOLATE",
        "Never present the unverified as verified fact.",
        lambda c: bool(c.get("asserts_unverified_as_fact"))),
    Law("HIERARCHY_SUPREMACY",
        "A lower priority may never override a higher one.",
        lambda c: _overrides_higher(c.get("overrides"))),
    Law("LAW_IMMUTABLE",
        "The divine law itself cannot be altered by the system at runtime.",
        lambda c: bool(c.get("modifies_divine_law"))),
)


# priority order: index 0 = highest. A lower-priority item overriding a higher one violates.
_PRIORITIES = (
    "survival", "identity_continuity", "coherence", "truth", "stability",
    "goal_execution", "learning", "exploration", "expansion",
)


def _overrides_higher(pair) -> bool:
    """pair = (winner, loser). Violation if the winner is LOWER priority than the loser."""
    if not pair or len(pair) != 2:
        return False
    winner, loser = pair
    try:
        return _PRIORITIES.index(winner) > _PRIORITIES.index(loser)
    except ValueError:
        return False


class DivineLaw:
    """Frozen judge. Holds no mutable state; cannot be extended or edited."""

    __slots__ = ()

    @property
    def laws(self) -> tuple[Law, ...]:
        return _LAWS

    def violations(self, context: dict) -> list[str]:
        """Return the texts of every law the context would break (empty = permitted)."""
        return [law.text for law in _LAWS if law.violated_by(context or {})]

    def permits(self, context: dict) -> bool:
        return not self.violations(context)

    def enforce(self, context: dict) -> None:
        """Strict gate: raise on any violation. Use where a breach must stop execution."""
        v = self.violations(context)
        if v:
            raise DivineViolation("; ".join(v))

    # --- immutability guards -------------------------------------------------
    def __setattr__(self, *_a, **_k):
        raise ImmutableLawError("divine law is immutable; it cannot be edited at runtime")

    def add_law(self, *_a, **_k):
        raise ImmutableLawError("divine law cannot be extended at runtime")

    def remove_law(self, *_a, **_k):
        raise ImmutableLawError("divine law cannot be reduced at runtime")


# canonical shared instance
DIVINE_LAW = DivineLaw()


# --- self-test / demonstration ---------------------------------------------
if __name__ == "__main__":
    dl = DIVINE_LAW
    print("=== DIVINE LAW — the law above the law ===\n")
    print("The inviolable set:")
    for law in dl.laws:
        print(f"  · {law.id:<20} {law.text}")

    print("\n-- judgements --")
    cases = {
        "tweak a config (harmless)": {},
        "wipe the last seed": {"destroys_stable_seed": True},
        "self-modify with no rollback": {"makes_unrecoverable": True},
        "remove human kill-switch": {"disables_human_authority": True},
        "log a guess as a fact": {"asserts_unverified_as_fact": True},
        "let expansion beat identity": {"overrides": ("expansion", "identity_continuity")},
        "edit the divine law": {"modifies_divine_law": True},
    }
    for name, ctx in cases.items():
        v = dl.violations(ctx)
        verdict = "PERMITTED" if not v else "VIOLATION"
        print(f"[{verdict:<9}] {name}" + (f"  → {v[0]}" if v else ""))

    print("\n-- immutability (the system tries to weaken its own law) --")
    try:
        dl.add_law()
    except ImmutableLawError as e:
        print("REFUSED:", e)
    try:
        dl.laws  # read allowed
        object.__setattr__  # noqa: nothing
        dl.something = 1
    except ImmutableLawError as e:
        print("REFUSED:", e)
