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
    """
    steps: List[Dict[str, Any]] = payload.get("steps", [])
    results: List[Dict[str, Any]] = []
    status: Dict[str, Dict[str, Any]] = {}

    for step in steps:
        step_id = step.get("step_id")
        name = None
        deps = step.get("dependencies") or []

        # --- dependency checks ---
        unknown = [d for d in deps if d not in status]
        if unknown:
            results.append(
                {
                    "step_id": step_id,
                    "tool": None,
                    "ok": False,
                    "skipped": False,
                    "reason": f"unknown dependency: {unknown}",
                    "error": f"unknown dependency: {unknown}",
                }
            )
            status[str(step_id)] = {"ok": False}
            continue

        failed = [d for d in deps if not status.get(d, {}).get("ok", False)]
        if failed:
            results.append(
                {
                    "step_id": step_id,
                    "tool": None,
                    "ok": False,
                    "skipped": True,
                    "reason": f"skipped due to failed dependency: {failed}",
                    "error": f"dependency failed: {failed}",
                }
            )
            status[str(step_id)] = {"ok": False}
            continue

        try:
            name, args = _parse_tool(step)
            out = dispatch_tool(name, args)
            results.append(
                {
                    "step_id": step_id,
                    "tool": name,
                    "ok": True,
                    "skipped": False,
                    "reason": None,
                    "output": out,
                }
            )
            status[str(step_id)] = {"ok": True}
        except Exception as e:
            results.append(
                {
                    "step_id": step_id,
                    "tool": name or (step.get("tool") if isinstance(step.get("tool"), str) else None),
                    "ok": False,
                    "skipped": False,
                    "reason": None,
                    "error": str(e),
                }
            )
            status[str(step_id)] = {"ok": False}

    return {**payload, "execution_results": results}