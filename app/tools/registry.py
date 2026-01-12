from __future__ import annotations

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
    Export tool specs for planner prompt if needed.
    """
    return [
        {"name": t.name, "description": t.description, "args_schema": t.args_schema}
        for t in _TOOL_REGISTRY.values()
    ]


def dispatch_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    tool = get_tool(name)
    out = tool.run(args or {})
    # 统一保证 dict 输出（便于 JSON 序列化）
    if isinstance(out, dict):
        return out
    return {"result": out}


def bootstrap_default_tools() -> None:
    register(ECHO_TOOL)
    register(TIME_TOOL)


bootstrap_default_tools()