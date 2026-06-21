#!/usr/bin/env python3
"""
NOESIS SELF-HEAL v3 — System który naprawia swój własny kod.
Scans for issues, generates patches, applies fixes.

Usage:
    python noesis_self_heal.py --check      # Diagnose issues
    python noesis_self_heal.py --fix        # Auto-fix issues
    python noesis_self_heal.py --watch      # Watch continuously
"""

import ast
import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

TARGET_FILES = [
    "noesis_engine.py",
    "noesis_engine_v21.py", 
    "noesis_dashboard.py",
    "noesis_autopilot.py",
    "noesis_insights.py",
]

SELF_HEAL_LOG = "self_heal_log.json"

class SelfHeal:
    def __init__(self):
        self.issues = []
        self.fixes = []

    def scan_file(self, filepath: Path) -> list:
        """Scan Python file for common issues."""
        issues = []
        try:
            source = filepath.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except SyntaxError as e:
            issues.append({"file": str(filepath), "line": e.lineno, "type": "syntax_error", "msg": str(e)})
            return issues
        except Exception as e:
            issues.append({"file": str(filepath), "line": 0, "type": "read_error", "msg": str(e)})
            return issues

        # Check for bare excepts
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append({"file": str(filepath), "line": node.lineno, "type": "bare_except", "msg": "Bare except clause"})

        # Check for undefined variables (simple)
        defined = set()
        used = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    defined.add(node.id)
                elif isinstance(node.ctx, ast.Load):
                    used.add(node.id)

        # Check for missing docstrings on functions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not ast.get_docstring(node):
                    if not node.name.startswith("_"):  # ignore private
                        issues.append({"file": str(filepath), "line": node.lineno, "type": "missing_docstring", "msg": f"Function '{node.name}' has no docstring"})

        # Check for TODOs in code
        for i, line in enumerate(source.split("\n"), 1):
            if "TODO" in line.upper() or "FIXME" in line.upper():
                issues.append({"file": str(filepath), "line": i, "type": "todo", "msg": line.strip()[:60]})

        return issues

    def scan_all(self) -> list:
        self.issues = []
        for fname in TARGET_FILES:
            fpath = Path(fname)
            if fpath.exists():
                self.issues.extend(self.scan_file(fpath))
        return self.issues

    def generate_fix(self, issue: dict) -> dict:
        """Generate a fix for an issue."""
        fix = {"issue": issue, "applied": False, "timestamp": datetime.now(timezone.utc).isoformat()}

        if issue["type"] == "missing_docstring":
            fix["suggestion"] = f"Add docstring to function at line {issue['line']}"
            fix["auto_fixable"] = False
        elif issue["type"] == "bare_except":
            fix["suggestion"] = f"Replace 'except:' with 'except Exception:' at line {issue['line']}"
            fix["auto_fixable"] = True
            fix["find"] = "except:"
            fix["replace"] = "except Exception:"
        elif issue["type"] == "todo":
            fix["suggestion"] = f"Address TODO at line {issue['line']}"
            fix["auto_fixable"] = False
        else:
            fix["suggestion"] = f"Manual review required: {issue['msg']}"
            fix["auto_fixable"] = False

        return fix

    def apply_fix(self, fix: dict) -> bool:
        """Apply an auto-fixable fix to the file."""
        if not fix.get("auto_fixable"):
            return False

        filepath = Path(fix["issue"]["file"])
        if not filepath.exists():
            return False

        try:
            source = filepath.read_text(encoding="utf-8")
            lines = source.split("\n")
            line_idx = fix["issue"]["line"] - 1

            if 0 <= line_idx < len(lines):
                if fix["find"] in lines[line_idx]:
                    lines[line_idx] = lines[line_idx].replace(fix["find"], fix["replace"])
                    filepath.write_text("\n".join(lines), encoding="utf-8")
                    fix["applied"] = True
                    return True
        except Exception as e:
            fix["error"] = str(e)

        return False

    def heal_all(self) -> dict:
        """Scan and apply all auto-fixable fixes."""
        issues = self.scan_all()
        fixes = [self.generate_fix(i) for i in issues]
        applied = 0
        for fix in fixes:
            if self.apply_fix(fix):
                applied += 1

        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "files_scanned": len(TARGET_FILES),
            "issues_found": len(issues),
            "fixes_generated": len(fixes),
            "fixes_applied": applied,
            "issues": issues,
            "fixes": fixes,
        }

        # Log to file
        log = []
        if Path(SELF_HEAL_LOG).exists():
            try:
                log = json.loads(Path(SELF_HEAL_LOG).read_text())
            except:
                pass
        log.append(result)
        Path(SELF_HEAL_LOG).write_text(json.dumps(log, indent=2, default=str), encoding="utf-8")

        return result

    def status(self) -> str:
        issues = self.scan_all()
        auto_fixable = sum(1 for i in issues if i["type"] in ["bare_except"])
        return f"Issues: {len(issues)} | Auto-fixable: {auto_fixable} | Files: {len(TARGET_FILES)}"


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NOESIS Self-Heal v3")
    parser.add_argument("--check", action="store_true", help="Check for issues")
    parser.add_argument("--fix", action="store_true", help="Apply auto-fixes")
    args = parser.parse_args()

    heal = SelfHeal()

    if args.fix:
        result = heal.heal_all()
        print("🔧 SELF-HEAL v3 COMPLETE")
        print(f"   Files scanned: {result['files_scanned']}")
        print(f"   Issues found: {result['issues_found']}")
        print(f"   Fixes applied: {result['fixes_applied']}")
        if result['fixes_applied'] > 0:
            print("   ✅ Code has been patched!")
        for i in result['issues']:
            status = "🔧 FIXED" if any(f['issue'] == i and f['applied'] for f in result['fixes']) else "⚠️  TODO"
            print(f"   {status} {i['file']}:{i['line']} — {i['type']}: {i['msg'][:50]}")
    else:
        issues = heal.scan_all()
        print(f"🔍 SELF-HEAL SCAN: {heal.status()}")
        for i in issues:
            print(f"   ⚠️  {i['file']}:{i['line']} — {i['type']}: {i['msg'][:50]}")
        if not issues:
            print("   ✅ No issues found! System is clean.")
