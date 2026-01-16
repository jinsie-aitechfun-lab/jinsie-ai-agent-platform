#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple


@dataclass(frozen=True)
class CheckResult:
    ok: bool
    message: str
    details: Dict[str, Any]


# ✅ 改为与你现有结构匹配：app/prompts/pcl/*.py
DEFAULT_MODE_PATHS: Dict[str, str] = {
    "system": "app/prompts/pcl/system.py",
    "task": "app/prompts/pcl/task.py",
    "schema": "app/prompts/pcl/schema.py",
    "validator": "app/prompts/pcl/validator.py",
    "router": "app/prompts/pcl/router.py",
    "tool": "app/prompts/pcl/tool.py",
    "memory": "app/prompts/pcl/memory.py",
    "fallback": "app/prompts/pcl/fallback.py",
    "safety": "app/prompts/pcl/safety.py",
    "multi_agent": "app/prompts/pcl/multi_agent.py",
}

INJECTION_HINT_TARGETS: List[str] = [
    "app/workflow/runner.py",
    "app/agents/runner.py",
    "app/agents/plan_executor.py",
]

INJECTION_HINT_PATTERNS: Dict[str, List[re.Pattern]] = {
    "system": [re.compile(r"system", re.IGNORECASE)],
    "schema": [re.compile(r"schema|json", re.IGNORECASE)],
    "router": [re.compile(r"route|router|tool_name", re.IGNORECASE)],
    "validator": [re.compile(r"validate|validator|repair", re.IGNORECASE)],
    "fallback": [re.compile(r"fallback|degrad|clarif", re.IGNORECASE)],
    "safety": [re.compile(r"safety|policy|refus", re.IGNORECASE)],
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def check_files_exist(repo_root: Path) -> Tuple[bool, Dict[str, Any]]:
    missing: Dict[str, str] = {}
    present: Dict[str, str] = {}
    for mode, rel in DEFAULT_MODE_PATHS.items():
        p = repo_root / rel
        if p.exists() and p.is_file():
            present[mode] = rel
        else:
            missing[mode] = rel
    return len(missing) == 0, {"present": present, "missing": missing}


def scan_injection_hints(repo_root: Path) -> Dict[str, Any]:
    targets: List[Path] = []
    for rel in INJECTION_HINT_TARGETS:
        p = repo_root / rel
        if p.exists() and p.is_file():
            targets.append(p)

    hits: Dict[str, List[Dict[str, str]]] = {k: [] for k in INJECTION_HINT_PATTERNS.keys()}

    for t in targets:
        text = read_text(t)
        for mode, patterns in INJECTION_HINT_PATTERNS.items():
            for pat in patterns:
                if pat.search(text):
                    hits[mode].append(
                        {
                            "file": str(t.relative_to(repo_root)),
                            "pattern": pat.pattern,
                        }
                    )
                    break

    return {
        "targets": [str(t.relative_to(repo_root)) for t in targets],
        "hits": hits,
        "note": "Hint scan is best-effort only (non-blocking).",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify Prompt Control Layer (PCL) presence and integration hints."
    )
    parser.add_argument("--repo-root", default=".", help="Path to repository root.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists():
        print(f"[FAIL] repo root does not exist: {repo_root}", file=sys.stderr)
        return 2

    ok_files, file_details = check_files_exist(repo_root)
    hint_details = scan_injection_hints(repo_root)

    result = CheckResult(
        ok=ok_files,
        message="PCL files present (10/10)."
        if ok_files
        else "PCL files missing. Create the missing prompt mode files.",
        details={
            "repo_root": str(repo_root),
            "file_check": file_details,
            "integration_hints": hint_details,
            "modes_expected": DEFAULT_MODE_PATHS,
        },
    )

    if args.json:
        print(
            json.dumps(
                {"ok": result.ok, "message": result.message, "details": result.details},
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        if result.ok:
            print("[PASS]", result.message)
        else:
            print("[FAIL]", result.message)
            missing = result.details["file_check"]["missing"]
            for mode, rel in missing.items():
                print(f"  - missing: {mode:>11} -> {rel}")

        print()
        print("[INFO] Integration hint scan (non-blocking):")
        targets = result.details["integration_hints"].get("targets", [])
        print("  targets:", ", ".join(targets) if targets else "(none)")
        hits = result.details["integration_hints"].get("hits", {})
        for mode, items in hits.items():
            if items:
                sample = items[0]
                print(
                    f"  - hint: {mode:>11} found in {sample['file']} (pattern: {sample['pattern']})"
                )

    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
