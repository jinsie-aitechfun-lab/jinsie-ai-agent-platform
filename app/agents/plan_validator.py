from __future__ import annotations

from typing import Any


def validate_plan_payload(
    payload: dict[str, Any],
    *,
    strict_tool_object: bool = True,
    strict_dep_order: bool = True,
    known_tools: set[str] | None = None,
) -> list[str]:
    """
    Plan payload contract validation.

    - Validates top-level shape and required fields
    - Validates per-step schema (including tool shape)
    - Enforces dependency integrity
    - Enforces step_id sequencing when using `step_{k}` convention
    - Optionally enforces tool object-form and dependency ordering
    """
    errors: list[str] = []

    if not isinstance(payload, dict):
        return ["payload must be an object"]

    # ---- top-level required fields ----
    required_top = ["task_summary", "steps", "assumptions", "risks"]
    for k in required_top:
        if k not in payload:
            errors.append(f"missing top-level field: {k}")

    if errors:
        return errors

    if not isinstance(payload["task_summary"], str) or not payload["task_summary"].strip():
        errors.append("task_summary must be a non-empty string")

    steps = payload.get("steps")
    if not isinstance(steps, list) or len(steps) == 0:
        errors.append("steps must be a non-empty array")
        return errors

    assumptions = payload.get("assumptions")
    if not isinstance(assumptions, list) or not all(isinstance(x, str) for x in assumptions):
        errors.append("assumptions must be an array of strings")

    risks = payload.get("risks")
    if not isinstance(risks, list) or not all(isinstance(x, str) for x in risks):
        errors.append("risks must be an array of strings")

    # ---- collect step_ids & basic shape checks ----
    step_ids: list[str] = []
    for i, s in enumerate(steps):
        if not isinstance(s, dict):
            errors.append(f"steps[{i}] must be an object")
            continue

        sid = s.get("step_id")
        if not isinstance(sid, str) or not sid.strip():
            errors.append(f"steps[{i}].step_id must be a non-empty string")
        else:
            step_ids.append(sid)

    # uniqueness
    if len(step_ids) != len(set(step_ids)):
        errors.append("step_id must be unique across steps")

    declared = set(step_ids)
    index_by_step_id = {sid: idx for idx, sid in enumerate(step_ids)}

    # ---- per-step schema & semantic checks ----
    required_step_fields = [
        "step_id",
        "title",
        "description",
        "dependencies",
        "deliverable",
        "acceptance",
        "tool",
    ]

    for i, s in enumerate(steps):
        if not isinstance(s, dict):
            continue

        for k in required_step_fields:
            if k not in s:
                errors.append(f"steps[{i}] missing field: {k}")

        # step_id already checked in collection step

        # required string fields
        for k in ["title", "description", "deliverable", "acceptance"]:
            if k in s and (not isinstance(s[k], str) or not s[k].strip()):
                errors.append(f"steps[{i}].{k} must be a non-empty string")

        # dependencies
        deps = s.get("dependencies", [])
        if deps is None:
            deps = []
        if not isinstance(deps, list):
            errors.append(f"steps[{i}].dependencies must be an array")
            deps = []
        else:
            for j, d in enumerate(deps):
                if not isinstance(d, str) or not d.strip():
                    errors.append(f"steps[{i}].dependencies[{j}] must be a non-empty string")
                    continue

                if d not in declared:
                    errors.append(f"steps[{i}] has unknown dependency: {d}")
                    continue

                # Enforce dependency order: dependencies must reference earlier steps only
                if strict_dep_order and d in index_by_step_id:
                    if index_by_step_id[d] >= i:
                        errors.append(f"steps[{i}] has forward dependency: {d}")

        # tool
        tool = s.get("tool")
        if tool is None:
            errors.append(f"steps[{i}] missing required field: tool")
        else:
            if isinstance(tool, str):
                # Executor may support string form, but planner contract can require object form.
                if strict_tool_object:
                    errors.append(f"steps[{i}].tool must be an object (string form is not allowed)")
                else:
                    if not tool.strip():
                        errors.append(f"steps[{i}].tool must be a non-empty string")
                    else:
                        if known_tools is not None and tool.strip() not in known_tools:
                            errors.append(f"steps[{i}] has unknown tool: {tool.strip()}")
                            
                    args = s.get("args")
                    if args is not None and not isinstance(args, dict):
                        errors.append(f"steps[{i}].args must be an object when provided")
            elif isinstance(tool, dict):
                name = tool.get("name")
                args = tool.get("args", {})
                if not isinstance(name, str) or not name.strip():
                    errors.append(f"steps[{i}].tool.name must be a non-empty string")
                else:
                    if known_tools is not None and name.strip() not in known_tools:
                        errors.append(f"steps[{i}] has unknown tool: {name.strip()}")
                if args is None:
                    args = {}
                if not isinstance(args, dict):
                    errors.append(f"steps[{i}].tool.args must be an object")

                # Avoid ambiguity: step.args and tool.args should not both exist
                if "args" in s:
                    errors.append(f"steps[{i}] must not provide both step.args and tool.args")
            else:
                errors.append(f"steps[{i}].tool must be a string or an object")

    # ---- step_id sequencing contract when using step_{k} convention ----
    # Prevent plans like: step_2/step_3 without step_1, or step_1/step_3 (gap).
    nums: list[int] = []
    for sid in step_ids:
        if sid.startswith("step_"):
            tail = sid[len("step_") :]
            if tail.isdigit():
                nums.append(int(tail))

    if nums:
        nums_sorted = sorted(nums)
        if nums_sorted[0] != 1:
            errors.append("step_id sequence must start from step_1")
        else:
            for a, b in zip(nums_sorted, nums_sorted[1:]):
                if b != a + 1:
                    errors.append("step_id sequence must be contiguous: step_1..step_N")
                    break

    return errors


def validate_execution_results(execution_results: list[dict[str, Any]]) -> list[str]:
    """
    Validate executor outputs for the execution contract.

    Requirements:
    - execution_results is a non-empty list
    - `__meta__` appears exactly once and must be the last item
    - per-item `ok` and `skipped` must exist
    - skipped=True => ok must be False
    - ok=True => error must be absent or None
    - failed and not skipped => must have error or reason
    """
    errors: list[str] = []

    if not isinstance(execution_results, list):
        return ["execution_results must be an array"]
    if len(execution_results) == 0:
        return ["execution_results must not be empty"]

    # __meta__ must be last and appear exactly once
    meta_indices = [
        i
        for i, r in enumerate(execution_results)
        if isinstance(r, dict) and r.get("step_id") == "__meta__"
    ]
    if len(meta_indices) != 1:
        errors.append("__meta__ must appear exactly once in execution_results")
    else:
        if meta_indices[0] != len(execution_results) - 1:
            errors.append("__meta__ must be the last item in execution_results")

    # per-item shape
    for i, r in enumerate(execution_results):
        if not isinstance(r, dict):
            errors.append(f"execution_results[{i}] must be an object")
            continue

        sid = r.get("step_id")
        if sid != "__meta__":
            if not isinstance(sid, str) or not sid.strip():
                errors.append(f"execution_results[{i}].step_id must be a non-empty string")

        if "ok" not in r:
            errors.append(f"execution_results[{i}] missing required field: ok")
        if "skipped" not in r:
            errors.append(f"execution_results[{i}] missing required field: skipped")

        ok = bool(r.get("ok"))
        skipped = bool(r.get("skipped"))

        if skipped and ok:
            errors.append(f"execution_results[{i}] invalid: skipped=True requires ok=False")

        if ok and ("error" in r and r.get("error") is not None):
            errors.append(f"execution_results[{i}] invalid: ok=True must not include error")

        if (not ok) and (not skipped):
            if (r.get("error") is None) and (r.get("reason") is None):
                errors.append(f"execution_results[{i}] invalid: failed step should include error or reason")

    # optional meta fields validation
    if meta_indices:
        meta = execution_results[meta_indices[0]]
        if isinstance(meta, dict):
            ts = meta.get("task_status")
            if ts is not None and ts not in ("COMPLETED", "PARTIAL", "FAILED", "BLOCKED"):
                errors.append("__meta__.task_status must be one of COMPLETED/PARTIAL/FAILED/BLOCKED")

            stats = meta.get("stats")
            if stats is not None:
                if not isinstance(stats, dict):
                    errors.append("__meta__.stats must be an object")
                else:
                    for k in ("total_steps", "ok", "skipped", "failed"):
                        if k not in stats:
                            errors.append(f"__meta__.stats missing field: {k}")

    return errors
