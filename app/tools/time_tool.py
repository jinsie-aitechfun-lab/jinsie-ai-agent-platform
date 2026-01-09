from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from app.tools.base import ToolSpec


def _run_time(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple local tool. Later you can replace it with:
    - external API
    - system clock formatting rules
    - timezone conversion
    """
    # default: ISO8601 in UTC
    now = datetime.now(timezone.utc).isoformat()
    return {"now_utc": now}


TIME_TOOL = ToolSpec(
    name="get_time",
    description="Get current time in UTC (ISO8601).",
    args_schema={
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
    handler=_run_time,
)
