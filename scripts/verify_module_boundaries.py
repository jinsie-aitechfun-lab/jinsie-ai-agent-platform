from __future__ import annotations

"""
Minimal module-boundary verifier.

Goal:
- Catch obvious forbidden imports early (before codebase grows).
- Keep rules simple and explicit (no AST, no heavy deps).

Run:
  PYTHONPATH=. python scripts/verify_module_boundaries.py
Exit code:
  0 = PASS
  1 = FAIL
"""

from pathlib import Path
import re
import sys
from typing import Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]


def iter_py_files(base: Path) -> Iterable[Path]:
    if not base.exists():
        return []
    return (p for p in base.rglob("*.py") if p.is_file())


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def normalize_import_lines(text: str) -> str:
    # We only need a light scan; keep original for line-number reporting.
    return text


def check_rules() -> List[str]:
    violations: List[str] = []

    # Rule 1: tool_runtime must not import agents/orchestration.
    # app/tools/* must not import app.agents.*
    tools_dir = ROOT / "app" / "tools"
    for f in iter_py_files(tools_dir):
        t = normalize_import_lines(read_text(f))
        if re.search(r"^\s*(from|import)\s+app\.agents\b", t, flags=re.M):
            violations.append(f"[R1] tools must not import agents: {f.relative_to(ROOT)}")

    # Rule 2: contract_prompt (plan_validator) must not import runner/executor.
    pv = ROOT / "app" / "agents" / "plan_validator.py"
    if pv.exists():
        t = normalize_import_lines(read_text(pv))
        if re.search(r"^\s*(from|import)\s+app\.agents\.runner\b", t, flags=re.M):
            violations.append("[R2] plan_validator must not import runner")
        if re.search(r"^\s*(from|import)\s+app\.agents\.plan_executor\b", t, flags=re.M):
            violations.append("[R2] plan_validator must not import plan_executor")

    # Rule 3: entry_shell (scripts) must not import app.tools directly.
    scripts_dir = ROOT / "scripts"
    for f in iter_py_files(scripts_dir):
        # allow this verifier itself to scan tools if needed later (currently it doesn't)
        if f.name == "verify_module_boundaries.py":
            continue
        t = normalize_import_lines(read_text(f))
        if re.search(r"^\s*(from|import)\s+app\.tools\b", t, flags=re.M):
            violations.append(f"[R3] scripts must not import tools directly: {f.relative_to(ROOT)}")

    return violations


def main() -> int:
    violations = check_rules()
    if violations:
        print("[FAIL] module boundary violations found:")
        for v in violations:
            print(f" - {v}")
        return 1

    print("[PASS] module boundaries verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
