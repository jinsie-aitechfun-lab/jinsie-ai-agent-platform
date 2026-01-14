from __future__ import annotations
# Module: tool_runtime
# Boundary: do NOT import app.agents/* (tools must be reusable and execution-agnostic)
# See: docs/architecture/modules.md
from typing import Any, Dict, List

from app.tools.base import ToolSpec
from app.tools.echo_tool import ECHO_TOOL
from app.tools.time_tool import TIME_TOOL


_TOOL_REGISTRY: Dict[str, ToolSpec] = {}


def register(tool: ToolSpec) -> None:
    if not tool.name:
        raise ValueError("Tool name is required.")
    _TOOL_REGISTRY[tool.name] = tool


def get_tool(name: str) -> ToolSpec:
    tool = _TOOL_REGISTRY.get(name)
    if not tool:
        raise ValueError(f"Unknown tool: {name}")
    return tool


def list_tools() -> List[Dict[str, Any]]:
    """
    Export canonical tool specs for planner prompt.
    Hide compatibility alias keys (e.g. time_tool/get_time_tool).
    """
    out: List[Dict[str, Any]] = []
    seen: set[str] = set()

    for key, t in _TOOL_REGISTRY.items():
        # 只展示“主名”条目：key 必须等于 tool.name
        # alias key（time_tool/get_time_tool）会被跳过
        if key != t.name:
            continue
        if t.name in seen:
            continue
        seen.add(t.name)
        out.append({"name": t.name, "description": t.description, "args_schema": t.args_schema})

    return out


def dispatch_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    tool = get_tool(name)
    out = tool.run(args or {})
    if isinstance(out, dict):
        return out
    return {"result": out}


def bootstrap_default_tools() -> None:
    register(ECHO_TOOL)
    register(TIME_TOOL)

    # compatibility aliases (older prompts / model drift)
    _TOOL_REGISTRY["time_tool"] = TIME_TOOL
    _TOOL_REGISTRY["get_time_tool"] = TIME_TOOL


bootstrap_default_tools()
