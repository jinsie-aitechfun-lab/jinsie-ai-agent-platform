from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.tools.registry import dispatch_tool


def _parse_tool(step: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """
    Support two formats:

    1) "tool": "echo_tool", and optional "args": {...}
    2) "tool": {"name": "echo_tool", "args": {...}}
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


def execute_plan(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute tools described in payload["steps"][].tool
    Returns: payload + execution_results (JSON-safe)

    Execution semantics (Day7):
    - unknown dependency -> fail-fast for that step (do not execute)
    - dependency failed/skipped -> skip that step (do not execute)
    """
    steps: List[Dict[str, Any]] = payload.get("steps", [])
    results: List[Dict[str, Any]] = []

    # Precompute all declared step_ids (for dependency existence check)
    declared_ids: List[str] = []
    for s in steps:
        sid = s.get("step_id")
        if isinstance(sid, str) and sid.strip():
            declared_ids.append(sid)

    # Track step status by step_id
    status: Dict[str, Dict[str, Any]] = {}  # {step_id: {"ok": bool, "skipped": bool}}

    for step in steps:
        step_id = step.get("step_id")
        deps = step.get("dependencies") or []
        name = None

        # Default result shape (stable fields)
        base: Dict[str, Any] = {
            "step_id": step_id,
            "tool": None,
            "ok": True,
            "skipped": False,
            "reason": None,
        }

        # --- dependency existence check ---
        unknown = []
        if isinstance(deps, list):
            for d in deps:
                if isinstance(d, str) and d not in declared_ids:
                    unknown.append(d)
        else:
            # schema should prevent this, but keep safe
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
                status[step_id] = {"ok": False, "skipped": False}
            continue

        # --- dependency success check (failed or skipped -> skip current) ---
        failed_deps = []
        if isinstance(deps, list):
            for d in deps:
                st = status.get(d)
                # If dependency hasn't run yet (out-of-order), treat as failed prerequisite.
                if not st or not st.get("ok", False) or st.get("skipped", False):
                    failed_deps.append(d)

        if failed_deps:
            r = {
                **base,
                "ok": False,
                "skipped": True,
                "reason": f"dependency not satisfied: {failed_deps}",
            }
            results.append(r)
            if isinstance(step_id, str):
                status[step_id] = {"ok": False, "skipped": True}
            continue

        # --- execute tool ---
        try:
            name, args = _parse_tool(step)
            out = dispatch_tool(name, args)
            r = {
                **base,
                "tool": name,
                "ok": True,
                "skipped": False,
                "reason": None,
                "output": out,
            }
            results.append(r)
            if isinstance(step_id, str):
                status[step_id] = {"ok": True, "skipped": False}
        except Exception as e:
            r = {
                **base,
                "tool": name or (step.get("tool") if isinstance(step.get("tool"), str) else None),
                "ok": False,
                "skipped": False,
                "reason": None,
                "error": str(e),
            }
            results.append(r)
            if isinstance(step_id, str):
                status[step_id] = {"ok": False, "skipped": False}

    return {**payload, "execution_results": results}
