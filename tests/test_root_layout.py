"""The repo root stays scannable: swarm dumps live under archive/."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_venture_records_left_the_root():
    assert list(ROOT.glob("venture_*.json")) == []
    archived = list((ROOT / "archive" / "ventures").glob("venture_*.json"))
    assert len(archived) >= 200


def test_snapshot_dumps_left_the_root():
    for name in ("brain_snapshot.json", "noesis_brain_export.json", "noesis_brain_v3.json"):
        assert not (ROOT / name).exists()
        assert (ROOT / "archive" / "snapshots" / name).is_file()
    assert not (ROOT / "session-ses_0dc0.md").exists()
    assert (ROOT / "archive" / "sessions" / "session-ses_0dc0.md").is_file()


def test_live_entrypoints_stay_importable_from_root():
    for name in (
        "README.md",
        "requirements.txt",
        "noesis_autopilot.py",
        "noesis_insights.py",
        "noesis_kernel.py",
        "divine_law.py",
        "venture-swarm.py",
    ):
        assert (ROOT / name).is_file(), name


def test_swarm_writes_records_under_archive():
    text = (ROOT / "venture-swarm.py").read_text(encoding="utf-8")
    assert 'VENTURE_RECORD_DIR = ROOT / "archive" / "ventures"' in text
    assert 'ROOT / f"venture_' not in text
