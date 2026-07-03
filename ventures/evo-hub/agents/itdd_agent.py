#!/usr/bin/env python3
"""
ITDD Agent for EVO-HUB
Enforces test-first workflow across all EVO-HUB development.

Usage:
    python agents/itdd_agent.py check          # Run all ITDD checks
    python agents/itdd_agent.py red <feature>  # Generate red spec template
    python agents/itdd_agent.py status         # Show ITDD compliance
"""
import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List

class ITDDAgent:
    """Agent enforcing ITDD discipline."""
    
    def __init__(self, hub_path: Path = None):
        self.hub = hub_path or Path(__file__).parent.parent
        self.tests_dir = self.hub / "tests"
        self.score = {"red": 0, "green": 0, "refactor": 0, "total": 0}
    
    def check(self) -> Dict:
        """Run ITDD test suite and report compliance."""
        print("🧪 ITDD Agent: Running compliance checks...")
        
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(self.tests_dir), "-v", "--tb=short"],
            capture_output=True, text=True, cwd=str(self.hub)
        )
        
        # Parse results
        lines = result.stdout.split("\n")
        for line in lines:
            if "passed" in line and "failed" in line:
                print(f"   {line}")
            elif line.startswith("FAILED"):
                self.score["red"] += 1
                self.score["total"] += 1
            elif line.startswith("PASSED"):
                self.score["green"] += 1
                self.score["total"] += 1
        
        if result.returncode == 0:
            self.score["refactor"] = 1
        
        return {
            "compliant": result.returncode == 0,
            "score": self.score,
            "stdout": result.stdout[-500:],
            "stderr": result.stderr[-200:]
        }
    
    def generate_red_spec(self, feature_name: str) -> str:
        """Generate a failing test template for a new feature."""
        spec = f"""def test_{feature_name.lower().replace(' ', '_')}():
    \"\"\"RED SPEC: {feature_name}
    
    Acceptance criteria:
    - TODO: Define expected behavior
    - TODO: Define input/output contract
    - TODO: Define error conditions
    \"\"\"\n    from ventures.evo_hub.backend.main import app  # adjust import
    # Write assertion that will fail until feature is implemented
    assert False, "RED: {feature_name} not yet implemented"
"""
        spec_file = self.tests_dir / f"test_{feature_name.lower().replace(' ', '_')}.py"
        spec_file.write_text(spec, encoding="utf-8")
        print(f"📝 RED spec generated: {spec_file}")
        return str(spec_file)
    
    def status(self) -> Dict:
        """Show current ITDD compliance status."""
        status = {
            "tests_dir": str(self.tests_dir),
            "test_files": [f.name for f in self.tests_dir.glob("test_*.py")],
            "compliant": self.check()["compliant"],
            "score": self.score
        }
        print(json.dumps(status, indent=2))
        return status


def main():
    import argparse
    parser = argparse.ArgumentParser(description="ITDD Agent for EVO-HUB")
    parser.add_argument("action", choices=["check", "red", "status"])
    parser.add_argument("feature", nargs="?", help="Feature name for red spec")
    args = parser.parse_args()
    
    agent = ITDDAgent()
    
    if args.action == "check":
        result = agent.check()
        sys.exit(0 if result["compliant"] else 1)
    elif args.action == "red":
        if not args.feature:
            print("Usage: python itdd_agent.py red <feature_name>")
            sys.exit(1)
        agent.generate_red_spec(args.feature)
    elif args.action == "status":
        agent.status()


if __name__ == "__main__":
    main()
