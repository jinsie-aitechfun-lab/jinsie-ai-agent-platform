from __future__ import annotations

import json
from typing import Any, Dict, Literal, Tuple

from app.agents.plan_executor import execute_plan
from app.agents.plan_validator import validate_execution_results, validate_plan_payload


Expectation = Literal["REJECT", "FAILED", "BLOCKED"]
PlanPolicy = Literal["REQUIRE_VALID", "ALLOW_ERRORS"]


def _print(title: str, obj: Any) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def _base_step(
    step_id: str,
    *,
    title: str,
    dependencies: list[str],
    tool_name: str,
    tool_args: dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return {
        "step_id": step_id,
        "title": title,
        "description": f"Execute {tool_name}.",
        "dependencies": dependencies,
        "deliverable": f"Output from {tool_name}.",
        "acceptance": "Tool execution result is captured in execution_results.",
        "tool": {"name": tool_name, "args": tool_args or {}},
    }


def _base_payload(task_summary: str, steps: list[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "task_summary": task_summary,
        "assumptions": ["未知"],
        "risks": ["未知"],
        "steps": steps,
    }


def _assert_task_status(meta: Dict[str, Any], expected: str) -> list[str]:
    errs: list[str] = []
    actual = meta.get("task_status")
    if actual != expected:
        errs.append(f"task_status expected {expected}, got {actual}")
    return errs


def main() -> int:
    # (case_name, payload, expected_task_status, plan_policy)
    cases: list[Tuple[str, Dict[str, Any], Expectation, PlanPolicy]] = []

    # Case 0: step_id sequencing contract failure -> REJECT at contract layer
    cases.append(
        (
            "missing_step_1",
            _base_payload(
                "missing step_1 should be rejected by plan contract",
                steps=[
                    _base_step(
                        "step_2",
                        title="start from step_2 (invalid)",
                        dependencies=[],
                        tool_name="get_time",
                    )
                ],
            ),
            "REJECT",
            "REQUIRE_VALID",
        )
    )

    # Case 1: unknown tool -> executor marks step failed; downstream skipped -> FAILED
    cases.append(
        (
            "unknown_tool_should_fail",
            _base_payload(
                "unknown tool should fail (not blocked)",
                steps=[
                    _base_step(
                        "step_1",
                        title="try unknown tool",
                        dependencies=[],
                        tool_name="no_such_tool",  # intentionally not in registry
                    ),
                    _base_step(
                        "step_2",
                        title="downstream depends on step_1",
                        dependencies=["step_1"],
                        tool_name="get_time",
                    ),
                ],
            ),
            "FAILED",
            "REQUIRE_VALID",
        )
    )

    # Case 2: unknown dependency -> contract flags; executor fail-fast -> BLOCKED
    # We *intentionally* allow plan errors for this case to verify executor behavior.
    cases.append(
        (
            "unknown_dependency_should_block",
            _base_payload(
                "unknown dependency should block",
                steps=[
                    _base_step(
                        "step_1",
                        title="bad deps",
                        dependencies=["step_X"],  # intentionally unknown
                        tool_name="get_time",
                    )
                ],
            ),
            "BLOCKED",
            "ALLOW_ERRORS",
        )
    )

    for name, payload, expected, plan_policy in cases:
        _print(f"[{name}] payload", payload)

        plan_errors = validate_plan_payload(payload, strict_tool_object=True, strict_dep_order=True)
        _print(f"[{name}] payload validation errors", plan_errors)

        if expected == "REJECT":
            if not plan_errors:
                print(f"\n[FAIL] [{name}] expected plan contract rejection, but got no errors")
                return 1
            continue

        if plan_policy == "REQUIRE_VALID" and plan_errors:
            print(f"\n[FAIL] [{name}] plan contract validation failed")
            return 1

        # Execute even if plan_errors exist when policy allows it
        out = execute_plan(payload)
        exec_results = out.get("execution_results", [])
        _print(f"[{name}] execution_results", exec_results)

        sem_errors = validate_execution_results(exec_results)
        _print(f"[{name}] execution_results semantic errors", sem_errors)
        if sem_errors:
            print(f"\n[FAIL] [{name}] execution_results semantic validation failed")
            return 1

        if not exec_results or not isinstance(exec_results[-1], dict) or exec_results[-1].get("step_id") != "__meta__":
            print(f"\n[FAIL] [{name}] missing __meta__ in execution_results")
            return 1

        meta = exec_results[-1]
        ts_errs = _assert_task_status(meta, expected)
        _print(f"[{name}] task_status assertion errors", ts_errs)
        if ts_errs:
            print(f"\n[FAIL] [{name}] task_status assertion failed")
            return 1

    print("\n[PASS] contract execution semantics verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
