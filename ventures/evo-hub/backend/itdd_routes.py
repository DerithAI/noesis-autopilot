"""
ITDD Routes — compliance scoreboard per venture.
Używa lokalnego ITDDAgenta i subprocess pytest.
"""
import subprocess
import sys
from pathlib import Path
from fastapi import APIRouter
from typing import Dict, List

router = APIRouter(prefix="/api/itdd", tags=["itdd"])

REPO_ROOT = Path(__file__).parent.parent.parent.parent

VENTURE_TEST_MAP = {
    "Task priority notifier": REPO_ROOT / "ventures" / "task-priority-notifier",
    "Quiz generator bot": REPO_ROOT / "ventures" / "quiz-generator-bot",
    "LeadGenTrackerAPI": REPO_ROOT / "ventures" / "leadgentrackerapi",
    "Auto-fill private keys scanner": REPO_ROOT / "ventures" / "auto-fill-private-keys-scanner",
    "personalized_workout": REPO_ROOT / "ventures" / "personalized_workout",
    "Personalized Evo Learning Path": REPO_ROOT / "ventures" / "personalized-evo-learning-path",
    "evo-hub": REPO_ROOT / "ventures" / "evo-hub",
}

@router.get("/scoreboard")
async def itdd_scoreboard() -> List[Dict]:
    """ITDD compliance per venture — red/green badges."""
    results = []
    for name, path in VENTURE_TEST_MAP.items():
        entry = {"venture": name, "path": str(path), "compliant": False, "tests": 0, "passed": 0, "failed": 0}
        if not path.exists():
            entry["note"] = "no_tests_directory"
            results.append(entry)
            continue
        test_dirs = [d for d in [path / "tests", path / "test"] if d.exists()]
        if not test_dirs:
            entry["note"] = "no_test_files"
            results.append(entry)
            continue
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest"] + [str(d) for d in test_dirs] + ["-q", "--tb=no"],
                capture_output=True, text=True, timeout=60,
                cwd=str(path)
            )
            output = result.stdout
            # Parse pytest summary like "3 passed in 0.42s"
            import re
            m = re.search(r'(\d+) passed', output)
            passed = int(m.group(1)) if m else 0
            m2 = re.search(r'(\d+) failed', output)
            failed = int(m2.group(1)) if m2 else 0
            entry["tests"] = passed + failed
            entry["passed"] = passed
            entry["failed"] = failed
            entry["compliant"] = failed == 0 and passed > 0
        except Exception as e:
            entry["note"] = str(e)
        results.append(entry)
    return results

@router.get("/status")
async def itdd_global_status() -> Dict:
    """Global ITDD status across all ventures."""
    board = await itdd_scoreboard()
    total = len(board)
    compliant = sum(1 for b in board if b["compliant"])
    with_tests = sum(1 for b in board if b["tests"] > 0)
    return {
        "total_ventures": total,
        "compliant": compliant,
        "with_tests": with_tests,
        "coverage_ratio": round(with_tests / total, 2) if total else 0,
        "compliance_ratio": round(compliant / total, 2) if total else 0,
        "scoreboard": board
    }
