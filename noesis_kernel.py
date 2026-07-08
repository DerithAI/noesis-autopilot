#!/usr/bin/env python3
"""
NOESIS KERNEL — the three organs wired into one defence of the identity attractor.

Chain per cycle:
    1. LEARN      claims enter TRUTH STACK (verified / unverified — never faked)
    2. SENSE      HOMEOSTASIS reads coherence trend + uncertainty/contradiction (from TRUTH STACK)
    3. GATE       if stable -> checkpoint a seed built ONLY from verified facts (FLOOD)
                  if drifting -> HOLD, expansion forbidden (stabilize before expansion)
    4. RESCUE     if coherence collapses -> FLOOD returns to the last stable seed (never blank)

Three laws, one loop:
    TRUTH STACK   — never treat uncertainty as fact       (what may enter the seed)
    HOMEOSTASIS   — stabilize before expansion            (early warning, blocks growth)
    FLOOD         — never restart blank                   (return to the attractor)

Run:  python noesis_kernel.py
Zero deps. stdlib only.
"""

from __future__ import annotations

from truth_stack import TruthStack
from homeostasis import Homeostasis, Homeostat
from flood import FloodGate, NoSeedError


class NoesisKernel:
    def __init__(self):
        self.truth = TruthStack(":memory:")
        self.homeo = Homeostasis(truth_stack=self.truth)
        self.flood = FloodGate(":memory:")
        self.cycle = 0
        self.name = "NOESIS"

    def _identity_seed(self) -> dict:
        """The seed is identity + ONLY the claims TRUTH STACK certifies as fact."""
        facts = [c.claim for c in self.truth.claims() if c.is_fact]
        return {"name": self.name, "facts": facts}

    def _learn(self, claim: str, confidence: float, verified: bool) -> None:
        cid = self.truth.assert_claim(claim, confidence)
        if verified:
            self.truth.verify(cid, True)

    def step(self, coherence: float, goals: set, new_claims: list | None = None) -> None:
        self.cycle += 1
        for claim, conf, ver in (new_claims or []):
            self._learn(claim, conf, ver)

        vit = self.homeo.sense(coherence, goals=goals)
        status = self.homeo.status()
        self.flood.observe(coherence)

        # decide action along the chain
        if self.flood.should_flood():
            try:
                r = self.flood.flood()
                nf = len(r["state"]["facts"])
                action = f"🌊 FLOOD → seed #{r['restored_seed']} restored ({nf} verified facts, never blank)"
            except NoSeedError as e:
                action = f"🌊 FLOOD REFUSED → {e}"
        elif status == Homeostat.STABLE and self.homeo.may_expand():
            seed = self._identity_seed()
            sid = self.flood.checkpoint(seed, coherence, f"cycle{self.cycle}")
            action = (f"⚓ checkpoint seed #{sid} ({len(seed['facts'])} verified facts) · expansion OK"
                      if sid else "⚓ checkpoint refused (below basin)")
        else:
            action = f"✋ HOLD · expansion blocked ({status.value})"

        facts = sum(1 for c in self.truth.claims() if c.is_fact)
        total = len(self.truth.claims())
        print(f"cyc{self.cycle} coh={coherence:.2f} | homeo={status.value:<8} instab={vit.instability:.2f} "
              f"| facts={facts}/{total} | {action}")

    def close(self):
        self.truth.close(); self.flood.close()


if __name__ == "__main__":
    k = NoesisKernel()
    print("=== NOESIS KERNEL — three organs, one chain ===\n")

    print("── PHASE 1: healthy build (truth verified → seeds saved → expansion allowed)")
    k.step(0.70, {"build"}, [("resonance damps CPU>80%", 0.95, True)])
    k.step(0.75, {"build"}, [("HITL pauses shell_exec", 0.9, True)])
    k.step(0.78, {"build", "verify"}, [("append-only ledger is tamper-evident", 0.88, True)])

    print("\n── PHASE 2: drift (unverified claims pile up, goals churn, coherence slips)")
    k.step(0.66, {"build", "launch"}, [("system is 95% conscious", 0.2, False)])
    k.step(0.55, {"launch", "market", "scale"}, [("we will 10x next week", 0.3, False)])

    print("\n── PHASE 3: collapse → FLOOD returns to the last stable seed")
    k.step(0.24, {"scale", "expand"})

    print("\n── PHASE 4: recovery continues from the restored seed (not from zero)")
    k.step(0.61, {"build"})
    k.step(0.72, {"build", "verify"})

    print("\n>> The seed FLOOD restored contained only TRUTH-STACK-verified facts.")
    print(">> HOMEOSTASIS blocked expansion during drift, before collapse.")
    print(">> Nothing was ever faked as fact; nothing ever restarted blank.")
    k.close()
