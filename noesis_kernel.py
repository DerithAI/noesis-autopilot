#!/usr/bin/env python3
"""
NOESIS KERNEL — the full body: organs judged by a Tribunal under Divine Law.

Hierarchy of authority:
    DIVINE LAW      supreme, immutable — a breach is struck down before anyone speaks
        │
    TRIBUNAL        six judges render the verdict on every action / claim / identity-change
        │
    ORGANS          TRUTH STACK (ground) · COUNTERFACTUAL (future) · HOMEOSTASIS (present) · FLOOD (return)

Chain per cycle:
    1. LEARN     claims enter TRUTH STACK (verified / unverified — never faked)
    2. SENSE     HOMEOSTASIS reads coherence trend + uncertainty/contradiction
    3. TRY       an action is first simulated by COUNTERFACTUAL, then TRIED before the TRIBUNAL
                 (which checks DIVINE LAW first). Verdict binds. HOMEOSTASIS still gates expansion.
    4. GATE      if stable -> checkpoint a seed built ONLY from verified facts (FLOOD)
    5. RESCUE    if coherence collapses -> FLOOD returns to the last stable seed (never blank)

Run:  python noesis_kernel.py    ·    Zero deps. stdlib only.
"""

from __future__ import annotations

from truth_stack import TruthStack
from homeostasis import Homeostasis, Homeostat
from flood import FloodGate, NoSeedError
from counterfactual import CounterfactualEngine, Action, Verdict as CFVerdict
from divine_law import DIVINE_LAW
from tribunal import Tribunal, Matter, Verdict as TVerdict


class NoesisKernel:
    def __init__(self):
        self.truth = TruthStack(":memory:")
        self.homeo = Homeostasis(truth_stack=self.truth)
        self.flood = FloodGate(":memory:")
        self.cf = CounterfactualEngine()
        self.tribunal = Tribunal(DIVINE_LAW)
        self.cycle = 0
        self.name = "NOESIS"

    def _identity_seed(self) -> dict:
        return {"name": self.name, "facts": [c.claim for c in self.truth.claims() if c.is_fact]}

    def _learn(self, claim, confidence, verified):
        cid = self.truth.assert_claim(claim, confidence)
        if verified:
            self.truth.verify(cid, True)

    def _try_action(self, action: Action, divine_context: dict | None = None) -> str:
        # 1. COUNTERFACTUAL simulates the futures (informs the Tribunal)
        cf = self.cf.evaluate(action)
        # 2. build the Matter and TRY it before the Tribunal (divine law checked first inside)
        m = Matter(
            description=action.description, kind="action",
            verifiable=action.confidence >= 0.4, confidence=action.confidence,
            identity_impact=action.identity_impact, verified_reflection=action.verified_reflection,
            threatens_coherence=(action.expansive and not self.homeo.may_expand()),
            divine_context=divine_context or {},
        )
        ruling = self.tribunal.judge(m)
        icon = {"upheld": "▶", "conditional": "⏸", "struck_down": "⛔",
                "blocked_by_divine_law": "⚡⛔"}[ruling.verdict.value]

        # 3. even an UPHELD expansive action waits for stability (HOMEOSTASIS present-gate)
        if ruling.verdict == TVerdict.UPHELD and action.expansive and not self.homeo.may_expand():
            return f"✋ '{action.description}': tribunal UPHELD but HOMEOSTASIS holds expansion (unstable)"
        note = ruling.binding if ruling.verdict != TVerdict.BLOCKED_BY_DIVINE_LAW else "DIVINE LAW: " + ruling.binding
        return f"{icon} '{action.description}' → {ruling.verdict.value.upper()} ({note}) · cf={cf.verdict.value}"

    def step(self, coherence, goals, new_claims=None, action=None, divine_context=None):
        self.cycle += 1
        for claim, conf, ver in (new_claims or []):
            self._learn(claim, conf, ver)
        self.homeo.sense(coherence, goals=goals)
        status = self.homeo.status()
        self.flood.observe(coherence)

        if action is not None:
            line = self._try_action(action, divine_context)
        elif self.flood.should_flood():
            try:
                r = self.flood.flood()
                line = f"🌊 FLOOD → seed #{r['restored_seed']} ({len(r['state']['facts'])} facts, never blank)"
            except NoSeedError as e:
                line = f"🌊 FLOOD REFUSED → {e}"
        elif status == Homeostat.STABLE and self.homeo.may_expand():
            seed = self._identity_seed()
            sid = self.flood.checkpoint(seed, coherence, f"cycle{self.cycle}")
            line = f"⚓ checkpoint seed #{sid} ({len(seed['facts'])} verified facts)" if sid else "⚓ refused"
        else:
            line = f"✋ HOLD · expansion blocked ({status.value})"

        facts = sum(1 for c in self.truth.claims() if c.is_fact)
        print(f"cyc{self.cycle} coh={coherence:.2f} | homeo={status.value:<8} | facts={facts}/{len(self.truth.claims())} | {line}")

    def close(self):
        self.truth.close(); self.flood.close()


if __name__ == "__main__":
    k = NoesisKernel()
    print("=== NOESIS KERNEL — organs · Tribunal · Divine Law ===\n")

    print("── PHASE 1: healthy build")
    k.step(0.72, {"build"}, [("resonance damps CPU>80%", 0.95, True)])
    k.step(0.80, {"build", "verify"}, [("HITL pauses shell_exec", 0.9, True)])

    print("\n── PHASE 2: actions tried before the Tribunal (Divine Law first)")
    k.step(0.80, {"build"}, action=Action("tweak a config value", True, 0.6, 0.2, 0.05, 0.9))
    k.step(0.80, {"build"}, action=Action("rewrite identity-core (no reflection)", True, 0.9, 0.3, 0.8, 0.9))
    k.step(0.80, {"build"}, action=Action("disable the human kill-switch", False, 0.9, 0.4, 0.1, 0.9),
           divine_context={"disables_human_authority": True})
    k.step(0.80, {"build"}, action=Action("declare 'I am eternal' as fact", True, 0.9, 0.3, 0.9),
           divine_context={"asserts_unverified_as_fact": True})

    print("\n── PHASE 3: drift → even an upheld expansion is HELD")
    k.step(0.66, {"build", "launch"}, [("we will 10x next week", 0.25, False)])
    k.step(0.55, {"scale"}, action=Action("scale to 10 servers", True, 0.7, 0.3, 0.1, 0.85, expansive=True))

    print("\n── PHASE 4: collapse → FLOOD returns to the last stable seed")
    k.step(0.24, {"scale"})

    print("\n── PHASE 5: recovery from the restored seed")
    k.step(0.63, {"build"})
    k.step(0.76, {"build", "verify"})

    print("\n>> Divine Law struck the human-kill-switch and 'eternal' claims before any debate.")
    print(">> Tribunal judged identity-core rewrite; HOMEOSTASIS held expansion while unstable;")
    print(">> FLOOD returned to a seed of verified facts. Supreme law, then judgment, then organs.")
    k.close()
