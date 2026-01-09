from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

JSONSchema = Dict[str, Any]


@dataclass(frozen=True)
class ToolSpec:
    """
    A structured tool contract.

    - name: tool identifier referenced by plan steps
    - description: shown to planner LLM
    - args_schema: JSONSchema-like dict
    - handler: callable(args) -> JSON-serializable output
    """
    name: str
    description: str
    args_schema: JSONSchema
    handler: Callable[[Dict[str, Any]], Any]

    def run(self, args: Optional[Dict[str, Any]] = None) -> Any:
        return self.handler(args or {})
