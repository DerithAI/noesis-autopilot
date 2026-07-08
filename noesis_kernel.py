#!/usr/bin/env python3
"""
NOESIS KERNEL — four organs wired into one defence of the identity attractor.

Chain per cycle:
    1. LEARN       claims enter TRUTH STACK (verified / unverified — never faked)
    2. SENSE       HOMEOSTASIS reads coherence trend + uncertainty/contradiction (from TRUTH STACK)
    3. JUDGE       if an action is proposed, COUNTERFACTUAL simulates its four futures
                   and the two gates decide together:
                     * COUNTERFACTUAL: reversible? severe? identity redline? confident?
                     * HOMEOSTASIS:    is the system even stable enough to act/expand?
    4. GATE        if stable -> checkpoint a seed built ONLY from verified facts (FLOOD)
    5. RESCUE      if coherence collapses -> FLOOD returns to the last stable seed (never blank)

Four laws, one loop:
    TRUTH STACK    — never treat uncertainty as fact       (the ground / what may enter)
    COUNTERFACTUAL — prefer reversible, never gamble identity (the future / before a step)
    HOMEOSTASIS    — stabilize before expansion            (the present / early warning)
    FLOOD          — never restart blank                   (the return / to the attractor)

Run:  python noesis_kernel.py
Zero deps. stdlib only.
"""

from __future__ import annotations

from truth_stack import TruthStack
from homeostasis import Homeostasis, Homeostat
from flood import FloodGate, NoSeedError
from counterfactual import CounterfactualEngine, Action, Verdict


class NoesisKernel:
    def __init__(self):
        self.truth = TruthStack(":memory:")
        self.homeo = Homeostasis(truth_stack=self.truth)
        self.flood = FloodGate(":memory:")
        self.cf = CounterfactualEngine()
        self.cycle = 0
        self.name = "NOESIS"

    def _identity_seed(self) -> dict:
        facts = [c.claim for c in self.truth.claims() if c.is_fact]
        return {"name": self.name, "facts": facts}

    def _learn(self, claim: str, confidence: float, verified: bool) -> None:
        cid = self.truth.assert_claim(claim, confidence)
        if verified:
            self.truth.verify(cid, True)

    def _judge_action(self, action: Action, may_expand: bool) -> str:
        """Two gates decide together: COUNTERFACTUAL (future) + HOMEOSTASIS (present)."""
        j = self.cf.evaluate(action)
        # present-gate overrides: an expansive act on an unstable system is refused
        if action.expansive and not may_expand and j.verdict == Verdict.PROCEED:
            return f"✋ action HELD — '{action.description}': counterfactual OK but system not stable (no expansion)"
        icon = {"proceed": "▶", "caution": "⏸", "simulate_more": "🔍", "block": "⛔"}[j.verdict.value]
        return f"{icon} action {j.verdict.value.upper()} — '{action.description}': {j.reasons[0]}"

    def step(self, coherence: float, goals: set, new_claims: list | None = None,
             action: Action | None = None) -> None:
        self.cycle += 1
        for claim, conf, ver in (new_claims or []):
            self._learn(claim, conf, ver)

        vit = self.homeo.sense(coherence, goals=goals)
        status = self.homeo.status()
        self.flood.observe(coherence)

        line = None
        if action is not None:
            line = self._judge_action(action, self.homeo.may_expand())
        elif self.flood.should_flood():
            try:
                r = self.flood.flood()
                nf = len(r["state"]["facts"])
                line = f"🌊 FLOOD → seed #{r['restored_seed']} restored ({nf} verified facts, never blank)"
            except NoSeedError as e:
                line = f"🌊 FLOOD REFUSED → {e}"
        elif status == Homeostat.STABLE and self.homeo.may_expand():
            seed = self._identity_seed()
            sid = self.flood.checkpoint(seed, coherence, f"cycle{self.cycle}")
            line = (f"⚓ checkpoint seed #{sid} ({len(seed['facts'])} verified facts)"
                    if sid else "⚓ checkpoint refused")
        else:
            line = f"✋ HOLD · expansion blocked ({status.value})"

        facts = sum(1 for c in self.truth.claims() if c.is_fact)
        total = len(self.truth.claims())
        print(f"cyc{self.cycle} coh={coherence:.2f} | homeo={status.value:<8} | facts={facts}/{total} | {line}")

    def close(self):
        self.truth.close(); self.flood.close()


if __name__ == "__main__":
    k = NoesisKernel()
    print("=== NOESIS KERNEL — four organs, one chain ===\n")

    print("── PHASE 1: healthy build (truth verified → seeds saved)")
    k.step(0.70, {"build"}, [("resonance damps CPU>80%", 0.95, True)])
    k.step(0.78, {"build", "verify"}, [("HITL pauses shell_exec", 0.9, True)])

    print("\n── PHASE 2: actions judged by COUNTERFACTUAL (future gate)")
    k.step(0.78, {"build"}, action=Action("tweak a config value", True, 0.6, 0.2, 0.05, 0.9))
    k.step(0.78, {"build"}, action=Action("deploy irreversible migration", False, 0.8, 0.7, 0.1, 0.85))
    k.step(0.78, {"build"}, action=Action("rewrite identity-core", False, 0.9, 0.5, 0.8, 0.9))

    print("\n── PHASE 3: drift → even a safe action is HELD (present gate: no expansion)")
    k.step(0.66, {"build", "launch"}, [("system is 95% conscious", 0.2, False)])
    k.step(0.55, {"launch", "scale"},
           action=Action("scale to 10 servers", True, 0.7, 0.3, 0.1, 0.8, expansive=True))

    print("\n── PHASE 4: collapse → FLOOD returns to the last stable seed")
    k.step(0.24, {"scale"})

    print("\n── PHASE 5: recovery from the restored seed (never from zero)")
    k.step(0.62, {"build"})
    k.step(0.74, {"build", "verify"})

    print("\n>> Future gate (COUNTERFACTUAL) blocks irreversible/identity-risking acts up front.")
    print(">> Present gate (HOMEOSTASIS) holds even safe expansion while unstable.")
    print(">> Ground (TRUTH STACK) keeps facts honest; return (FLOOD) never restarts blank.")
    k.close()
