from __future__ import annotations

from typing import Any, Dict

from app.tools.base import ToolSpec


def _echo_handler(args: Dict[str, Any]) -> Dict[str, Any]:
    text = args.get("text", "")
    return {"echo": text}


ECHO_TOOL = ToolSpec(
    name="echo_tool",
    description="Echo back the input text.",
    args_schema={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Text to echo"},
        },
        "required": ["text"],
        "additionalProperties": False,
    },
    handler=_echo_handler,
)
