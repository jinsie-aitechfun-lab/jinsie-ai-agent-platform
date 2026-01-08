from __future__ import annotations
from typing import Any, Dict


def echo_tool(text: str) -> Dict[str, Any]:
    return {"echo": text}
