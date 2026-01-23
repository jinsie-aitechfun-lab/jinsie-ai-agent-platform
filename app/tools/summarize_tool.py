from __future__ import annotations

from typing import Any, Dict, List

from app.tools.base import ToolSpec


def _coerce_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _normalize_text(x: Any) -> str:
    if isinstance(x, str):
        return x.strip()
    return str(x).strip()


def _extract_docs(args: Dict[str, Any]) -> List[Dict[str, Any]]:
    docs = args.get("docs")
    if not isinstance(docs, list):
        raise ValueError("summarize_tool: args.docs must be an array")
    out: List[Dict[str, Any]] = []
    for d in docs:
        if isinstance(d, dict):
            out.append(d)
    return out


def _summarize_handler(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic local summarizer (no LLM).

    Args:
    - docs: array of objects, each should include "content"
    - max_points: int (optional, default=2, range 1-5)

    Returns:
    - {"count": int, "points": [str, ...]}
    """
    docs = _extract_docs(args)

    max_points = _coerce_int(args.get("max_points", 2), default=2)
    if max_points <= 0:
        max_points = 2
    if max_points > 5:
        max_points = 5

    points: List[str] = []
    seen: set[str] = set()

    for d in docs:
        content = _normalize_text(d.get("content", ""))
        if not content:
            continue

        # simple normalization: collapse whitespace and bound length
        s = " ".join(content.split())
        if len(s) > 120:
            s = s[:117] + "..."

        if s in seen:
            continue
        seen.add(s)

        points.append(s)
        if len(points) >= max_points:
            break

    return {"count": len(points), "points": points}


SUMMARIZE_TOOL = ToolSpec(
    name="summarize_tool",
    description="Summarize docs into concise key points (deterministic, no LLM).",
    args_schema={
        "type": "object",
        "properties": {
            "docs": {
                "type": "array",
                "description": "Docs to summarize; each item should include content",
                "items": {"type": "object"},
            },
            "max_points": {
                "type": "integer",
                "description": "Max number of key points to output (1-5)",
                "default": 2,
            },
        },
        "required": ["docs"],
        "additionalProperties": False,
    },
    handler=_summarize_handler,
)
