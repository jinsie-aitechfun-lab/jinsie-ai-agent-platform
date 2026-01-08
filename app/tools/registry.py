from __future__ import annotations

from typing import Any, Callable, Dict

from app.tools.echo_tool import echo_tool

ToolFn = Callable[..., Dict[str, Any]]

TOOL_REGISTRY: Dict[str, ToolFn] = {
    "echo_tool": echo_tool,
}

def dispatch_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    fn = TOOL_REGISTRY.get(name)
    if not fn:
        raise ValueError(f"Unknown tool: {name}")
    return fn(**args)
