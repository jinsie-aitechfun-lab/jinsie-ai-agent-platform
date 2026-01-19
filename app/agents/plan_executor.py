from __future__ import annotations
# Module: execution_engine
# Boundary: do NOT import runner/entry_shell; do NOT own contract rules (keep those in plan_validator/prompt)
# See: docs/architecture/modules.md

from typing import Any, Optional, Tuple

from app.tools.registry import dispatch_tool


def _parse_tool(step: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """
    Support two formats:

    1) step["tool"] = "echo_tool", and optional step["args"] = {...}
    2) step["tool"] = {"name": "echo_tool", "args": {...}}
    """
    tool = step.get("tool")
    if not tool:
        raise ValueError("Missing step.tool")

    if isinstance(tool, str):
        return tool, (step.get("args") or {})

    if isinstance(tool, dict):
        name = tool.get("name")
        args = tool.get("args") or {}
        if not name or not isinstance(name, str):
            raise ValueError("tool.name must be a non-empty string")
        if not isinstance(args, dict):
            raise ValueError("tool.args must be an object")
        return name, args

    raise ValueError("step.tool must be a string or an object")


def _detect_degraded(tool_name: str, args: dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Best-effort degraded detection (no coupling to planner internals).

    We consider a step "degraded" when:
    - tool_name == "echo_tool"
    - args.text suggests "unknown tool" / "tool not found" fallback

    Returns: (degraded, degraded_reason, degraded_from)
    """
    if tool_name != "echo_tool":
        return False, None, None

    text = args.get("text")
    if not isinstance(text, str) or not text.strip():
        return False, None, None

    low = text.lower()

    triggers = [
        "不存在",
        "未实现",
        "unknown tool",
        "tool not found",
        "no_such_tool",
        "降级",
        "占位",
        "fallback",
    ]
    if not any(t in text for t in triggers) and not any(t in low for t in triggers):
        return False, None, None

    degraded_from: Optional[str] = None
    if "no_such_tool" in low:
        degraded_from = "no_such_tool"

    reason = "degraded: fallback-to-echo_tool (unknown tool or placeholder)"
    return True, reason, degraded_from


def compute_task_status(execution_results: list[dict[str, Any]]) -> str:
    """
    Compute overall task status from per-step execution_results.

    Status priority:
    1) BLOCKED: any step has unknown dependency OR is skipped due to dependency not satisfied (hard)
    2) FAILED: any step failed (ok=false) and not skipped
    3) PARTIAL: some ok and some skipped (including strict-degraded skips)
    4) COMPLETED: all ok

    Notes:
    - __meta__ result (if present) is ignored for status computation.
    - empty results => BLOCKED
    """
    if not execution_results:
        return "BLOCKED"

    any_ok = False
    any_skipped = False

    for r in execution_results:
        if r.get("step_id") == "__meta__":
            continue

        ok = bool(r.get("ok"))
        skipped = bool(r.get("skipped"))
        reason = (r.get("reason") or "")
        error = (r.get("error") or "")

        if ok:
            any_ok = True
            continue

        # not ok
        if skipped:
            any_skipped = True

            # strict degraded: not a "hard blocked" dependency, treat as PARTIAL
            if "dependency not satisfied (degraded)" in reason:
                continue

            # hard dependency not satisfied => BLOCKED
            if "dependency not satisfied" in reason:
                return "BLOCKED"
            continue

        # not ok and not skipped
        if "unknown dependency" in reason or "unknown dependency" in error:
            return "BLOCKED"

        return "FAILED"

    if any_skipped:
        return "PARTIAL"
    return "COMPLETED"


def execute_plan(payload: dict[str, Any], *, strict_degraded: bool = False) -> dict[str, Any]:
    """
    Execute tools described in payload["steps"][].tool
    Returns: payload + execution_results (JSON-safe)

    Execution semantics (contract):
    - unknown dependency -> fail-fast for that step (do not execute)
    - dependency failed/skipped -> skip that step (do not execute)
    - unknown tool -> mark that step failed; downstream deps will be skipped
    - append a __meta__ summary as the LAST execution_result

    Degraded semantics:
    - degraded means "tool ran ok, but semantics are a placeholder/fallback".

    strict_degraded:
    - False (default): degraded does NOT block downstream deps (current behavior)
    - True: degraded is treated as NOT satisfiable dependency for downstream steps
    """
    steps: list[dict[str, Any]] = payload.get("steps", []) or []
    results: list[dict[str, Any]] = []

    declared_ids: set[str] = set()
    for s in steps:
        sid = s.get("step_id")
        if isinstance(sid, str) and sid.strip():
            declared_ids.add(sid)

    # status for dependency checks
    status: dict[str, dict[str, Any]] = {}

    for step in steps:
        step_id = step.get("step_id")
        deps = step.get("dependencies") or []
        tool_name: Optional[str] = None

        base: dict[str, Any] = {
            "step_id": step_id,
            "tool": None,
            "ok": True,
            "skipped": False,
            "reason": None,
            "degraded": False,
            "degraded_reason": None,
            "degraded_from": None,
        }

        # --- dependency existence check ---
        unknown: list[str] = []
        if isinstance(deps, list):
            for d in deps:
                if isinstance(d, str) and d not in declared_ids:
                    unknown.append(d)
        else:
            unknown = ["<invalid dependencies>"]

        if unknown:
            r = {
                **base,
                "ok": False,
                "skipped": False,
                "reason": f"unknown dependency: {unknown}",
                "error": f"unknown dependency: {unknown}",
            }
            results.append(r)
            if isinstance(step_id, str):
                status[step_id] = {"ok": False, "skipped": False, "degraded": False}
            continue

        # --- dependency satisfiable check ---
        failed_deps: list[str] = []
        degraded_deps: list[str] = []

        if isinstance(deps, list):
            for d in deps:
                st = status.get(d)
                if (not st) or (not st.get("ok", False)) or st.get("skipped", False):
                    failed_deps.append(d)
                    continue
                if strict_degraded and st.get("degraded", False):
                    degraded_deps.append(d)

        if failed_deps or degraded_deps:
            if degraded_deps and not failed_deps:
                reason = f"dependency not satisfied (degraded): {degraded_deps}"
            else:
                # if any hard failed deps exist, we keep it as hard dependency not satisfied
                all_bad = failed_deps + degraded_deps
                reason = f"dependency not satisfied: {all_bad}"

            r = {
                **base,
                "ok": False,
                "skipped": True,
                "reason": reason,
            }
            results.append(r)
            if isinstance(step_id, str):
                status[step_id] = {"ok": False, "skipped": True, "degraded": False}
            continue

        # --- execute tool ---
        try:
            tool_name, args = _parse_tool(step)
            out = dispatch_tool(tool_name, args)

            degraded, degraded_reason, degraded_from = _detect_degraded(tool_name, args)

            r = {
                **base,
                "tool": tool_name,
                "ok": True,
                "skipped": False,
                "reason": None,
                "output": out,
                "degraded": degraded,
                "degraded_reason": degraded_reason,
                "degraded_from": degraded_from,
            }
            results.append(r)
            if isinstance(step_id, str):
                status[step_id] = {"ok": True, "skipped": False, "degraded": degraded}
        except Exception as e:
            inferred_tool = None
            if tool_name:
                inferred_tool = tool_name
            else:
                raw_tool = step.get("tool")
                if isinstance(raw_tool, str):
                    inferred_tool = raw_tool
                elif isinstance(raw_tool, dict):
                    maybe_name = raw_tool.get("name")
                    if isinstance(maybe_name, str):
                        inferred_tool = maybe_name

            r = {
                **base,
                "tool": inferred_tool,
                "ok": False,
                "skipped": False,
                "reason": None,
                "error": str(e),
            }
            results.append(r)
            if isinstance(step_id, str):
                status[step_id] = {"ok": False, "skipped": False, "degraded": False}

    task_status = compute_task_status(results)

    total_steps = sum(1 for r in results if r.get("step_id") != "__meta__")
    ok_count = sum(1 for r in results if r.get("step_id") != "__meta__" and r.get("ok") is True)
    skipped_count = sum(1 for r in results if r.get("step_id") != "__meta__" and r.get("skipped") is True)
    failed_count = sum(
        1
        for r in results
        if r.get("step_id") != "__meta__" and (not r.get("ok")) and (not r.get("skipped", False))
    )

    degraded_steps: list[str] = []
    for r in results:
        if r.get("step_id") == "__meta__":
            continue
        if r.get("degraded") is True:
            sid = r.get("step_id")
            if isinstance(sid, str):
                degraded_steps.append(sid)

    summary_reason = None
    if task_status == "PARTIAL":
        summary_reason = "some steps skipped"
    elif task_status == "FAILED":
        summary_reason = "one or more steps failed"
    elif task_status == "BLOCKED":
        summary_reason = "blocked by dependency resolution"

    blocked_steps: list[str] = []
    failed_steps: list[str] = []
    for r in results:
        sid = r.get("step_id")
        if sid == "__meta__":
            continue

        reason = (r.get("reason") or "")
        msg = reason + " " + (r.get("error") or "")

        # hard blocked only (exclude strict-degraded skips)
        if r.get("skipped") and "dependency not satisfied" in reason and "dependency not satisfied (degraded)" not in reason:
            if isinstance(sid, str):
                blocked_steps.append(sid)
        elif (not r.get("ok")) and (not r.get("skipped", False)):
            if "unknown dependency" in msg:
                if isinstance(sid, str):
                    blocked_steps.append(sid)
            else:
                if isinstance(sid, str):
                    failed_steps.append(sid)

    results.append(
        {
            "step_id": "__meta__",
            "tool": None,
            "ok": (task_status == "COMPLETED"),
            "skipped": False,
            "reason": summary_reason,
            "task_status": task_status,
            "stats": {
                "total_steps": total_steps,
                "ok": ok_count,
                "skipped": skipped_count,
                "failed": failed_count,
                "degraded_count": len(degraded_steps),
            },
            "degraded_steps": degraded_steps,
            "blocked_steps": blocked_steps,
            "failed_steps": failed_steps,
            "strict_degraded": strict_degraded,
        }
    )

    return {**payload, "execution_results": results}
