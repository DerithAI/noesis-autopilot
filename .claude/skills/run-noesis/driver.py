#!/usr/bin/env python3
"""
run-noesis driver — smoke harness for the NOESIS KERNEL.

NOESIS is a stdlib-only Python library: thirteen cognitive "organs" plus a kernel that
wires them into one loop. There is no GUI and no server — each organ is self-driving
(its `if __name__ == "__main__"` block is a self-test/demo). This harness runs every
organ's self-test and the full kernel loop, checks exit code + an expected marker, and
reports PASS/FAIL.

Usage:  python .claude/skills/run-noesis/driver.py
Exit 0 = all organs beat; non-zero = something is wrong.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]   # .../noesis-autopilot

# (module, marker that must appear in its output)
ORGANS = [
    ("divine_law.py",     "VIOLATION"),
    ("perception.py",     "PERCEPTION pipeline"),
    ("truth_stack.py",    "REFUSED"),
    ("memory_tree.py",    "REFUSED"),
    ("identity_core.py",  "REFUSED"),
    ("tribunal.py",       "BLOCKED_BY_DIVINE_LAW"),
    ("crown.py",          "CHOSE"),
    ("counterfactual.py", "BLOCK"),
    ("homeostasis.py",    "unstable"),
    ("flood.py",          "never restarted blank"),
    ("evolution.py",      "REFUSE"),
    ("noesis_kernel.py",  "beats as one"),
]


def run_one(module: str, marker: str) -> tuple[bool, str]:
    try:
        r = subprocess.run([sys.executable, module], cwd=REPO,
                           capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    if r.returncode != 0:
        return False, f"exit {r.returncode}: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ''}"
    if marker not in r.stdout:
        return False, f"marker '{marker}' not found in output"
    return True, "ok"


def main() -> int:
    print(f"run-noesis :: smoke harness  (repo: {REPO})\n")
    passed = 0
    failed = []
    for module, marker in ORGANS:
        ok, detail = run_one(module, marker)
        print(f"  [{'PASS' if ok else 'FAIL'}] {module:<20} {'' if ok else '— ' + detail}")
        if ok:
            passed += 1
        else:
            failed.append(module)
    total = len(ORGANS)
    print(f"\n{passed}/{total} organs beat.")
    if failed:
        print("FAILED:", ", ".join(failed))
        return 1
    print("NOESIS KERNEL: all organs operational. AUUU.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
