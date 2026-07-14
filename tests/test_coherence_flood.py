# Real tests for Organ XIV (Coherence Meter) and Organ XII (Flood) —
# coherence is MEASURED from state, and FLOOD provably recovers from
# injected incoherence by restoring the last stable seed.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from coherence import CoherenceMeter, WEIGHTS
from truth_stack import TruthStack
from identity_core import IdentityCore
from noesis_kernel import NoesisKernel


def _identity():
    return IdentityCore(name="NOESIS", origin="test", values=["truth"], constraints=[])


class TestCoherenceMeter:
    def test_weights_sum_to_one(self):
        assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9

    def test_fresh_boot_is_inside_seed_basin(self):
        truth = TruthStack(":memory:")
        r = CoherenceMeter().measure(truth, _identity(), {"build"})
        assert 0.55 <= r.coherence <= 1.0, "fresh boot must be able to checkpoint a seed"
        truth.close()

    def test_verified_facts_raise_coherence(self):
        truth = TruthStack(":memory:")
        meter = CoherenceMeter()
        before = meter.measure(truth, _identity(), {"build"}).coherence
        cid = truth.assert_claim("ledger is tamper-evident", 0.95)
        truth.verify(cid, True)
        after = meter.measure(truth, _identity(), {"build"}).coherence
        assert after > before
        truth.close()

    def test_refuted_claims_lower_coherence(self):
        truth = TruthStack(":memory:")
        meter = CoherenceMeter()
        identity = _identity()
        cid = truth.assert_claim("real fact", 0.95)
        truth.verify(cid, True)
        healthy = meter.measure(truth, identity, {"build"}).coherence
        for i in range(5):
            cid = truth.assert_claim(f"hallucination #{i}", 0.9)
            truth.verify(cid, False)
        poisoned = meter.measure(truth, identity, {"build"}).coherence
        assert poisoned < healthy - 0.2, "mass refutation must visibly tank coherence"
        truth.close()

    def test_goal_thrash_lowers_coherence(self):
        truth = TruthStack(":memory:")
        meter = CoherenceMeter()
        identity = _identity()
        meter.measure(truth, identity, {"build"})
        steady = meter.measure(truth, identity, {"build"}).coherence
        thrash = meter.measure(truth, identity, {"pivot", "rewrite", "scale"}).coherence
        assert thrash < steady
        truth.close()

    def test_report_is_auditable(self):
        truth = TruthStack(":memory:")
        r = CoherenceMeter().measure(truth, _identity(), {"build"})
        assert set(r.components) == set(WEIGHTS)
        assert "claims" in r.detail and "refuted" in r.detail
        truth.close()


class TestFloodRecovery:
    """End-to-end: healthy cycles checkpoint seeds; injected incoherence
    triggers FLOOD; FLOOD restores the exact last-stable state, never blank."""

    def test_flood_recovers_from_injected_incoherence(self):
        k = NoesisKernel()

        # healthy phase: verified truths, stable goals -> measured coherence is high
        r1 = k.step(goals={"build"}, verified=["HITL pauses shell_exec"])
        r2 = k.step(goals={"build"}, verified=["ledger is tamper-evident"])
        assert r1["coherence"] >= 0.55 and r2["coherence"] >= 0.55
        seed = k.flood.last_seed()
        assert seed is not None, "stable cycles must checkpoint a seed"
        stable_facts = set(seed.state["facts"])
        assert "HITL pauses shell_exec" in stable_facts

        # INJECT INCOHERENCE: the system's beliefs are mass-refuted
        for i in range(12):
            cid = k.truth.assert_claim(f"corrupted belief #{i}", 0.9)
            k.truth.verify(cid, False)

        # drive cycles with MEASURED (not injected) coherence — the kernel must
        # detect the collapse itself and FLOOD within a cycle
        flooded = None
        for goals in ({"pivot"}, {"rewrite"}, {"escape"}, {"abandon"}):
            r = k.step(goals=goals)
            if "FLOOD" in r["line"]:
                flooded = r
                break
        assert flooded, f"measured coherence never triggered FLOOD (last={r['coherence']})"
        assert flooded["coherence"] < 0.30, "FLOOD must fire from collapsed measurement"
        assert "seed #" in flooded["line"]
        restored = k.flood.last_seed()
        assert set(restored.state["facts"]) == stable_facts
        assert restored.state["identity"]["name"] == "NOESIS"

        # post-flood trajectory is back inside the basin
        assert k.flood.status().value == "stable"

        # GENUINE recovery: the poisoned beliefs were purged, so the next cycle's
        # MEASURED coherence is back inside the seed basin — not still collapsed
        r = k.step(goals={"recover"})
        assert r["coherence"] >= 0.55, f"post-flood measured coherence still low: {r['coherence']}"
        assert r["facts"] == r["claims"] == len(stable_facts)
        k.close()

    def test_flood_refuses_blank_restart(self):
        from flood import FloodGate, NoSeedError
        fg = FloodGate(":memory:")
        fg.observe(0.05)
        with pytest.raises(NoSeedError):
            fg.flood()
        fg.close()
