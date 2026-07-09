---
name: run-noesis
description: Run, test, drive, and smoke-check the NOESIS KERNEL — the thirteen-organ cognitive engine. Use when asked to run noesis, test the organs, drive the kernel, or verify the noesis-autopilot build.
---

# run-noesis

NOESIS is a **stdlib-only Python library**: thirteen cognitive "organs" (`truth_stack.py`,
`flood.py`, `homeostasis.py`, `counterfactual.py`, `divine_law.py`, `tribunal.py`,
`perception.py`, `identity_core.py`, `crown.py`, `memory_tree.py`, `evolution.py`) plus
`noesis_kernel.py` that wires them into one loop. No GUI, no server, no dependencies —
each organ is self-driving (its `__main__` block is a self-test/demo).

The driver is **`.claude/skills/run-noesis/driver.py`**: it runs every organ's self-test
and the full kernel loop as subprocesses, checks exit code + an expected marker, and
reports PASS/FAIL. Paths below are relative to the repo root (`noesis-autopilot/`).

Verified: Windows 11, Python 3.11.15, this session.

## Prerequisites

Python 3.10+ only. **No pip install** — zero third-party dependencies (stdlib + sqlite3).

```bash
python --version    # 3.10+ (tested on 3.11.15)
```

## Build

None. There is nothing to compile or bundle.

## Run (agent path) — smoke the whole body

```bash
python .claude/skills/run-noesis/driver.py
```

Expected tail:

```
12/12 organs beat.
NOESIS KERNEL: all organs operational. AUUU.
```

Exit 0 = all organs operational; non-zero = a failing organ is named.

## Direct invocation — drive one organ

Each organ runs standalone and prints its own demo (running a module file works from any
directory; importing organs in your own code needs cwd = repo root — see Gotchas):

```bash
python noesis_kernel.py     # full 13-organ loop, end-to-end demo
python truth_stack.py       # V  — never treat uncertainty as fact
python tribunal.py          # VIII — judges the Claude entity cards under Divine Law
python flood.py             # XII — never restart blank
```

To use an organ in code, import it (from the repo root):

```bash
python -c "from truth_stack import TruthStack; ts=TruthStack(':memory:'); print('ok')"
```

## Gotchas

- **Flat imports — the boundary is imports, not file-execution.** Organs import each other
  flatly (`from tribunal import ...`). Running a module *file* works from any directory —
  `python noesis_kernel.py` and even `python /abs/path/tribunal.py` both work, because Python
  puts the script's own dir on `sys.path[0]`. But **importing** an organ in your own code
  (`python -c "from truth_stack import ..."`) only resolves when your cwd is the repo root
  (or the repo is on `PYTHONPATH`). The driver sidesteps this entirely by launching with
  `cwd = repo root`.
- **No GUI/server to screenshot** — this is a library. "Driving" it = running the self-tests
  and the kernel loop, which is exactly what the driver does.
- **`.claude/` is gitignored in this repo** — the skill was force-added (`git add -f`).
- **`homeostasis.py` was calibrated after its first self-test refuted it** (it reported
  `stable` through a clear drift). If you edit its weights/thresholds, re-run and confirm it
  raises `watch`/`unstable` under drift before trusting it — the marker the driver checks is
  the word `unstable` appearing in its output.
- Git may warn `LF will be replaced by CRLF` on Windows — cosmetic, ignore.

## Troubleshooting

- `ModuleNotFoundError: No module named 'truth_stack'` → you tried to *import* an organ from
  a cwd other than the repo root. `cd` to the repo root, set `PYTHONPATH`, or use the driver
  (it sets `cwd`). Note: running a module *file* directly does not hit this.
- Driver prints `FAIL <module> — marker '...' not found` → that organ's self-test changed
  its output; open the module, run it directly, confirm behaviour, update the marker in
  `driver.py`.
