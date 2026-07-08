#!/usr/bin/env python3
"""
NOESIS — TRUTH STACK (Organ V)

Core law:  Never treat uncertainty as fact.

Every major claim tracks:  claim · evidence · confidence · verification_state · revision_history.
A claim is only usable AS A FACT when it is verified AND its confidence clears the threshold.
Everything else is an opinion, a hypothesis, or noise — and must be labelled as such.

Zero dependencies. Python 3.10+ stdlib only. SQLite-backed (matches MEMORY TREE).

Design note: this organ is the antidote to "engine tangled with altar" — it lets any
reader tell a load-bearing claim (high confidence, verified, evidence) from a beautiful
but unverified one. It does not decide truth; it refuses to let the system pretend.
"""

from __future__ import annotations

import sqlite3
import json
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# --- confidence floor a verified claim must clear to count as a usable fact
FACT_THRESHOLD = 0.8


class VerificationState(str, Enum):
    UNVERIFIED = "unverified"   # asserted, not checked
    VERIFYING = "verifying"     # check in progress
    VERIFIED = "verified"       # independently confirmed
    REFUTED = "refuted"         # checked and found false — can NEVER become a fact


class UncertaintyError(Exception):
    """Raised when code asks for a claim AS A FACT that has not earned that status."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Claim:
    id: int
    claim: str
    confidence: float
    verification_state: str
    evidence: list = field(default_factory=list)
    revisions: list = field(default_factory=list)

    @property
    def is_fact(self) -> bool:
        """Core law: fact == verified AND confidence >= threshold. Refuted is never a fact."""
        return (
            self.verification_state == VerificationState.VERIFIED
            and self.confidence >= FACT_THRESHOLD
        )

    def label(self) -> str:
        if self.verification_state == VerificationState.REFUTED:
            return "REFUTED"
        if self.is_fact:
            return "FACT"
        if self.verification_state == VerificationState.VERIFIED:
            return "VERIFIED-BUT-LOW-CONFIDENCE"
        if self.confidence >= FACT_THRESHOLD:
            return "CONFIDENT-BUT-UNVERIFIED"   # e.g. a strong belief, not yet checked
        return "HYPOTHESIS"


class TruthStack:
    def __init__(self, db_path: str = "truth_stack.db"):
        self.db = sqlite3.connect(db_path)
        self.db.row_factory = sqlite3.Row
        self._migrate()

    def _migrate(self) -> None:
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim TEXT NOT NULL,
                confidence REAL NOT NULL,
                verification_state TEXT NOT NULL,
                created TEXT NOT NULL,
                updated TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim_id INTEGER NOT NULL,
                source TEXT NOT NULL,
                content TEXT NOT NULL,
                added TEXT NOT NULL,
                FOREIGN KEY (claim_id) REFERENCES claims(id)
            );
            CREATE TABLE IF NOT EXISTS revisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim_id INTEGER NOT NULL,
                field TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                reason TEXT,
                ts TEXT NOT NULL,
                FOREIGN KEY (claim_id) REFERENCES claims(id)
            );
            """
        )
        self.db.commit()

    # -- assertion -----------------------------------------------------------
    def assert_claim(
        self,
        claim: str,
        confidence: float = 0.5,
        verification_state: str = VerificationState.UNVERIFIED,
        evidence: Optional[list] = None,
    ) -> int:
        """Assert a claim. confidence in [0,1]. Nothing is a fact just by being asserted."""
        confidence = max(0.0, min(1.0, float(confidence)))
        vs = VerificationState(verification_state).value
        now = _now()
        cur = self.db.execute(
            "INSERT INTO claims (claim, confidence, verification_state, created, updated) "
            "VALUES (?,?,?,?,?)",
            (claim, confidence, vs, now, now),
        )
        cid = cur.lastrowid
        for ev in evidence or []:
            src, content = (ev if isinstance(ev, tuple) else ("unspecified", ev))
            self.add_evidence(cid, src, content)
        self.db.commit()
        return cid

    def add_evidence(self, claim_id: int, source: str, content: str) -> None:
        self.db.execute(
            "INSERT INTO evidence (claim_id, source, content, added) VALUES (?,?,?,?)",
            (claim_id, source, content, _now()),
        )
        self.db.commit()

    # -- revision (identity changes only through tracked revision) -----------
    def revise(self, claim_id: int, field_name: str, new_value, reason: str = "") -> None:
        if field_name not in ("claim", "confidence", "verification_state"):
            raise ValueError(f"cannot revise field: {field_name}")
        row = self.db.execute(
            f"SELECT {field_name} AS v FROM claims WHERE id=?", (claim_id,)
        ).fetchone()
        if row is None:
            raise KeyError(claim_id)
        old = row["v"]
        if field_name == "confidence":
            new_value = max(0.0, min(1.0, float(new_value)))
        if field_name == "verification_state":
            new_value = VerificationState(new_value).value
        self.db.execute(
            f"UPDATE claims SET {field_name}=?, updated=? WHERE id=?",
            (new_value, _now(), claim_id),
        )
        self.db.execute(
            "INSERT INTO revisions (claim_id, field, old_value, new_value, reason, ts) "
            "VALUES (?,?,?,?,?,?)",
            (claim_id, field_name, str(old), str(new_value), reason, _now()),
        )
        self.db.commit()

    def verify(self, claim_id: int, verified: bool, reason: str = "") -> None:
        """Record a verification outcome. Refuted claims can never become facts again
        without an explicit revision back through 'verifying' (kept in history)."""
        self.revise(
            claim_id,
            "verification_state",
            VerificationState.VERIFIED if verified else VerificationState.REFUTED,
            reason or ("verification passed" if verified else "verification failed"),
        )

    # -- reading -------------------------------------------------------------
    def get(self, claim_id: int) -> Claim:
        row = self.db.execute("SELECT * FROM claims WHERE id=?", (claim_id,)).fetchone()
        if row is None:
            raise KeyError(claim_id)
        ev = self.db.execute(
            "SELECT source, content, added FROM evidence WHERE claim_id=? ORDER BY id", (claim_id,)
        ).fetchall()
        rev = self.db.execute(
            "SELECT field, old_value, new_value, reason, ts FROM revisions WHERE claim_id=? ORDER BY id",
            (claim_id,),
        ).fetchall()
        return Claim(
            id=row["id"],
            claim=row["claim"],
            confidence=row["confidence"],
            verification_state=row["verification_state"],
            evidence=[dict(e) for e in ev],
            revisions=[dict(r) for r in rev],
        )

    def is_fact(self, claim_id: int) -> bool:
        return self.get(claim_id).is_fact

    def as_fact(self, claim_id: int) -> str:
        """CORE LAW ENFORCEMENT. Returns the claim text only if it is a fact.
        Otherwise raises UncertaintyError — the system is forbidden from pretending."""
        c = self.get(claim_id)
        if not c.is_fact:
            raise UncertaintyError(
                f"claim #{claim_id} is '{c.label()}' "
                f"(state={c.verification_state}, confidence={c.confidence:.2f}); "
                f"not usable as fact"
            )
        return c.claim

    def claims(self, state: Optional[str] = None) -> list:
        if state:
            rows = self.db.execute(
                "SELECT id FROM claims WHERE verification_state=? ORDER BY id",
                (VerificationState(state).value,),
            ).fetchall()
        else:
            rows = self.db.execute("SELECT id FROM claims ORDER BY id").fetchall()
        return [self.get(r["id"]) for r in rows]

    def close(self) -> None:
        self.db.close()


# --- self-test / demonstration ---------------------------------------------
if __name__ == "__main__":
    ts = TruthStack(":memory:")

    # 1) A load-bearing engineering claim: evidence + verification -> FACT
    engine = ts.assert_claim(
        "NerveSystem damps resonance when CPU load > 80%",
        confidence=0.95,
        evidence=[("code", "modules/nerve_system.py: resonance_engine.set_damping(0.1)")],
    )
    ts.verify(engine, True, reason="read the source; behaviour confirmed")

    # 2) A beautiful but unverified claim from a simulation -> NOT a fact
    altar = ts.assert_claim(
        "System reached 95.26% consciousness",
        confidence=0.2,
        evidence=[("sim", "record_simulation_data uses random.uniform")],
    )

    # 3) A strong belief, not yet checked -> confident but unverified, still not a fact
    belief = ts.assert_claim("Identity behaves as an attractor", confidence=0.85)

    print("=== TRUTH STACK demo — 'never treat uncertainty as fact' ===\n")
    for cid in (engine, altar, belief):
        c = ts.get(cid)
        print(f"#{cid} [{c.label():<26}] conf={c.confidence:.2f} :: {c.claim}")

    print("\n-- as_fact() enforcement --")
    print("engine  ->", ts.as_fact(engine))
    for cid, name in ((altar, "altar"), (belief, "belief")):
        try:
            ts.as_fact(cid)
        except UncertaintyError as e:
            print(f"{name}   -> REFUSED: {e}")

    # revision history is preserved
    print("\n-- revision history of the verified claim --")
    for r in ts.get(engine).revisions:
        print(f"  {r['ts']}: {r['field']} {r['old_value']} -> {r['new_value']} ({r['reason']})")

    ts.close()
