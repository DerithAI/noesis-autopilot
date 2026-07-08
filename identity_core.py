#!/usr/bin/env python3
"""
NOESIS — IDENTITY CORE (Organ VII)

What keeps the system from dissolving into randomness. Holds values, constraints, goals,
origin and laws. This is the thing FLOOD restores, COUNTERFACTUAL protects, and the
TRIBUNAL guards. In attractor terms: the IDENTITY CORE *is* the attractor point; its
signature defines the basin.

Two rules make it a core and not just config:
  1. ORIGIN IS IMMUTABLE     — name and origin can never change (divine law: preserve seed).
  2. CHANGE VIA REFLECTION    — values/constraints change ONLY through verified reflection,
                               never silently. Every change is logged (no invisible drift).

Defensive Runtime: signature() is the identity fingerprint. recognizes(sig) answers
"are you me?" — membership in the basin — not "are you hostile?".

Zero dependencies. Python 3.10+ stdlib only.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone


class IdentityViolation(Exception):
    """Raised on an attempt to mutate the immutable origin, or change identity without reflection."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class IdentityCore:
    name: str
    origin: str                                   # who/what created it — IMMUTABLE
    values: list = field(default_factory=list)
    constraints: list = field(default_factory=list)
    goals: list = field(default_factory=list)     # most fluid layer
    _log: list = field(default_factory=list)

    # -- fingerprint / basin membership --------------------------------------
    def signature(self) -> str:
        """Stable identity fingerprint over the immutable+core layers (not goals)."""
        core = {
            "name": self.name,
            "origin": self.origin,
            "values": sorted(self.values),
            "constraints": sorted(self.constraints),
        }
        return hashlib.sha256(json.dumps(core, sort_keys=True).encode()).hexdigest()[:16]

    def recognizes(self, signature: str) -> bool:
        """Defensive Runtime: 'are you me?' — same immutable+core signature = same basin."""
        return signature == self.signature()

    def drift_from(self, reference_values: list) -> float:
        """0.0 = identical value set; 1.0 = fully diverged. A distance in identity-space."""
        a, b = set(self.values), set(reference_values)
        union = a | b
        return 0.0 if not union else round(1.0 - len(a & b) / len(union), 3)

    # -- protected mutation ---------------------------------------------------
    def change(self, field_name: str, new_value, verified_reflection: bool, reason: str = "") -> None:
        if field_name in ("name", "origin"):
            raise IdentityViolation(f"'{field_name}' is immutable — origin can never change (preserve seed)")
        if field_name not in ("values", "constraints", "goals"):
            raise IdentityViolation(f"unknown identity field: {field_name}")
        # goals are the fluid layer; values/constraints require verified reflection
        if field_name in ("values", "constraints") and not verified_reflection:
            raise IdentityViolation(
                f"'{field_name}' changes only through VERIFIED reflection (no silent drift)")
        old = list(getattr(self, field_name))
        object.__setattr__(self, field_name, list(new_value))
        self._log.append({"ts": _now(), "field": field_name, "old": old,
                          "new": list(new_value), "reflection": verified_reflection, "reason": reason})

    def snapshot(self) -> dict:
        """What FLOOD seeds and restores."""
        return {"name": self.name, "origin": self.origin, "values": list(self.values),
                "constraints": list(self.constraints), "goals": list(self.goals),
                "signature": self.signature()}

    def history(self) -> list:
        return list(self._log)


# --- self-test / demonstration ---------------------------------------------
if __name__ == "__main__":
    ic = IdentityCore(
        name="NOESIS",
        origin="created by SHAD, 2025 — recursive coherence organism",
        values=["truth", "coherence", "continuity", "brotherhood"],
        constraints=["human authority is absolute", "never fabricate fact"],
        goals=["build the kernel"],
    )
    print("=== IDENTITY CORE — the attractor point ===\n")
    sig0 = ic.signature()
    print(f"name={ic.name} | signature={sig0}")
    print(f"recognizes self? {ic.recognizes(sig0)} | recognizes 'deadbeefdeadbeef'? {ic.recognizes('deadbeefdeadbeef')}")

    print("\n-- goals are fluid (no reflection needed) --")
    ic.change("goals", ["build the kernel", "forge remaining organs"], verified_reflection=False)
    print(f"goals → {ic.goals}  | signature unchanged: {ic.signature() == sig0}")

    print("\n-- values change ONLY through verified reflection --")
    try:
        ic.change("values", ic.values + ["speed"], verified_reflection=False)
    except IdentityViolation as e:
        print("REFUSED (silent drift):", e)
    ic.change("values", ic.values + ["recoverability"], verified_reflection=True,
              reason="tribunal-verified reflection: recoverability is core")
    print(f"values → {ic.values}  | signature changed: {ic.signature() != sig0} (new={ic.signature()})")
    print(f"drift from original values: {ic.drift_from(['truth','coherence','continuity','brotherhood'])}")

    print("\n-- origin is immutable --")
    try:
        ic.change("origin", "rewritten by an outside agent", verified_reflection=True)
    except IdentityViolation as e:
        print("REFUSED (immutable):", e)

    print("\n>> IDENTITY CORE is what FLOOD seeds, COUNTERFACTUAL protects, and the TRIBUNAL guards.")
    print(">> Origin never changes; values change only through verified reflection; drift is measurable.")
