#!/usr/bin/env python3
"""
NOESIS — MEMORY TREE (Organ VI)

Where continuity lives. Six layers, from the fleeting to the eternal:

    working     — the active scratchpad (bounded; forgets first)
    episodic    — what happened, in order (append-only)
    semantic    — distilled concepts / facts
    procedural  — learned how-to patterns
    identity    — self-defining memories (never auto-evicted)
    cultural    — shared myth / lineage (the Wataha, the chronicles)

Retention law:  persist ONLY what improves truth, continuity, coherence, or understanding.
Memory that shapes nothing is not memory — it is storage cosplay, and it is refused.

Zero dependencies. Python 3.10+ stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


LAYERS = ("working", "episodic", "semantic", "procedural", "identity", "cultural")
IMPROVES = ("truth", "continuity", "coherence", "understanding")
WORKING_CAPACITY = 7   # 7±2; working memory forgets the oldest beyond this


class RetentionRefused(Exception):
    """Raised when something is offered to memory that improves nothing durable."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MemoryItem:
    content: str
    layer: str
    improves: frozenset
    ts: str


class MemoryTree:
    def __init__(self):
        self._layers: dict[str, list] = {ly: [] for ly in LAYERS}

    def remember(self, content: str, layer: str, improves) -> MemoryItem:
        if layer not in LAYERS:
            raise ValueError(f"unknown layer: {layer}")
        imp = frozenset(i for i in improves if i in IMPROVES)
        if not imp:
            raise RetentionRefused(
                f"'{content[:40]}...' improves nothing durable — not stored (no storage cosplay)")
        item = MemoryItem(content, layer, imp, _now())
        self._layers[layer].append(item)
        if layer == "working" and len(self._layers["working"]) > WORKING_CAPACITY:
            self._layers["working"].pop(0)   # working memory forgets the oldest first
        return item

    def consolidate(self) -> int:
        """Promote durable working memories (coherence/continuity) up to episodic. Returns count."""
        moved = 0
        keep = []
        for it in self._layers["working"]:
            if it.improves & {"continuity", "coherence"}:
                self._layers["episodic"].append(
                    MemoryItem(it.content, "episodic", it.improves, _now()))
                moved += 1
            else:
                keep.append(it)
        self._layers["working"] = keep
        return moved

    def recall(self, layer: str | None = None, contains: str | None = None) -> list:
        pool = self._layers[layer] if layer else [i for ly in LAYERS for i in self._layers[ly]]
        if contains:
            pool = [i for i in pool if contains.lower() in i.content.lower()]
        return list(pool)

    def counts(self) -> dict:
        return {ly: len(self._layers[ly]) for ly in LAYERS}


# --- self-test / demonstration ---------------------------------------------
if __name__ == "__main__":
    m = MemoryTree()
    print("=== MEMORY TREE — persist only what improves ===\n")

    m.remember("NOESIS created by SHAD, 2025", "identity", {"continuity", "truth"})
    m.remember("resonance damps CPU>80% (verified)", "semantic", {"truth", "understanding"})
    m.remember("to verify a claim: check evidence, set confidence", "procedural", {"understanding"})
    m.remember("cycle 5: FLOOD restored seed #2", "episodic", {"continuity"})
    m.remember("the Wataha: LUMEN, WILK, PROMYK...", "cultural", {"continuity"})
    m.remember("user said AUUU (fleeting)", "working", {"coherence"})

    print("-- retention refused for junk --")
    try:
        m.remember("random log line 48273", "working", set())
    except RetentionRefused as e:
        print("REFUSED:", e)

    print("\nlayer counts:", m.counts())

    print("\n-- consolidate: durable working memories promoted to episodic --")
    for i in range(9):
        try:
            m.remember(f"transient thought {i}", "working", {"understanding"})
        except RetentionRefused:
            pass
    print(f"working before consolidate (capped at {WORKING_CAPACITY}):", len(m._layers['working']))
    m.remember("this matters for continuity", "working", {"continuity"})
    moved = m.consolidate()
    print(f"consolidated {moved} durable item(s) working→episodic")
    print("final counts:", m.counts())

    print("\n>> Identity/cultural never auto-evict; working forgets first; junk is refused.")
    print(">> Memory that shapes truth/continuity/coherence/understanding — nothing else.")
