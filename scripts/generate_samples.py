from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


SAMPLES_DIR = Path("docs/samples")


def _write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_plan_sample() -> Dict[str, Any]:
    """
    A minimal plan payload sample that matches the plan contract.
    """
    return {
        "task_summary": "echo a short message",
        "assumptions": ["inputs are provided by user"],
        "risks": ["none"],
        "steps": [
            {
                "step_id": "step_1",
                "title": "echo the message",
                "description": "Call echo_tool with a short text.",
                "dependencies": [],
                "deliverable": "A tool output containing the echoed text.",
                "acceptance": "execution_results contains step_1 with ok=true and output.echo equals the input text.",
                "tool": {"name": "echo_tool", "args": {"text": "hello"}},
            }
        ],
    }


def build_execution_plan_sample() -> Dict[str, Any]:
    """
    A slightly richer plan payload sample that includes a dependency.
    """
    return {
        "task_summary": "echo a message then read current time",
        "assumptions": ["tool registry provides echo_tool and get_time"],
        "risks": ["time output format may vary by environment"],
        "steps": [
            {
                "step_id": "step_1",
                "title": "echo the message",
                "description": "Call echo_tool with a short text.",
                "dependencies": [],
                "deliverable": "A tool output containing the echoed text.",
                "acceptance": "execution_results contains step_1 ok=true and output.echo is present.",
                "tool": {"name": "echo_tool", "args": {"text": "hello"}},
            },
            {
                "step_id": "step_2",
                "title": "get current time",
                "description": "Call get_time after step_1 succeeds.",
                "dependencies": ["step_1"],
                "deliverable": "A tool output containing current time fields.",
                "acceptance": "execution_results contains step_2 ok=true and output is JSON-safe.",
                "tool": {"name": "get_time", "args": {}},
            },
        ],
    }


def main() -> int:
    plan_sample = build_plan_sample()
    exec_plan_sample = build_execution_plan_sample()

    _write_json(SAMPLES_DIR / "agent_plan_sample.json", plan_sample)
    _write_json(SAMPLES_DIR / "agent_execution_plan_sample.json", exec_plan_sample)

    print("[OK] generated samples:")
    print(" - docs/samples/agent_plan_sample.json")
    print(" - docs/samples/agent_execution_plan_sample.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
