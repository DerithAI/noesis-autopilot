"""Scaffold validation tests.

Validates the deploy scaffold of this venture:
Dockerfile, docker-compose.yml, requirements.txt, README.md.

Path-relative (tests/ lives inside the venture dir), stdlib + pytest only.
The same file is used verbatim in every venture.
"""
import re
from pathlib import Path

VENTURE_DIR = Path(__file__).resolve().parent.parent

# PEP 508-ish project name + optional extras + optional version spec.
REQUIREMENT_RE = re.compile(
    r"^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?"   # package name
    r"(\[[A-Za-z0-9._,\s-]+\])?"                    # optional extras
    r"\s*([<>=!~]=?\s*[A-Za-z0-9.*+!_-]+"           # optional version spec
    r"(\s*,\s*[<>=!~]=?\s*[A-Za-z0-9.*+!_-]+)*)?"
    r"\s*(;.*)?$"                                    # optional env marker
)


def _read(name: str) -> str:
    path = VENTURE_DIR / name
    assert path.is_file(), f"{name} is missing in {VENTURE_DIR}"
    return path.read_text(encoding="utf-8", errors="replace")


def test_dockerfile_exists_and_has_from():
    content = _read("Dockerfile")
    assert content.strip(), "Dockerfile is empty"
    from_lines = [
        line for line in content.splitlines()
        if line.strip().upper().startswith("FROM ")
    ]
    assert from_lines, "Dockerfile has no FROM line"


def test_docker_compose_parses():
    content = _read("docker-compose.yml")
    assert content.strip(), "docker-compose.yml is empty"
    try:
        import yaml  # PyYAML may not be installed; structural check below then.
    except ImportError:
        assert "services:" in content, "docker-compose.yml has no services: key"
    else:
        data = yaml.safe_load(content)
        assert isinstance(data, dict), "docker-compose.yml did not parse to a mapping"
        assert "services" in data, "docker-compose.yml has no services key"
        assert isinstance(data["services"], dict) and data["services"], \
            "docker-compose.yml services section is empty"


def test_requirements_lines_are_valid_tokens():
    content = _read("requirements.txt")
    lines = [
        line.strip() for line in content.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert lines, "requirements.txt has no requirements"
    for line in lines:
        assert REQUIREMENT_RE.match(line), f"invalid requirement line: {line!r}"


def test_readme_exists_and_non_empty():
    content = _read("README.md")
    assert content.strip(), "README.md is empty"
