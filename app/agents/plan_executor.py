from __future__ import annotations
from typing import Any, Dict, List
from app.tools.registry import dispatch_tool


def execute_plan(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute tools described in payload["steps"][].tool
    Returns: payload + execution_results (JSON-safe)
    """
    steps: List[Dict[str, Any]] = payload.get("steps", [])
    results: List[Dict[str, Any]] = []

    for step in steps:
        tool = step.get("tool")
        if not tool:
            continue

        name = tool.get("name")
        args = tool.get("args") or {}

        try:
            out = dispatch_tool(name, args)
            results.append({
                "step_id": step.get("step_id"),
                "tool": name,
                "ok": True,
                "output": out,
            })
        except Exception as e:
            results.append({
                "step_id": step.get("step_id"),
                "tool": name,
                "ok": False,
                "error": str(e),
            })

    # 不破坏原结构：在 payload 顶层加执行结果
    return {**payload, "execution_results": results}
