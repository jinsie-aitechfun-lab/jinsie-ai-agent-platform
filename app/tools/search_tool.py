from __future__ import annotations

from typing import Any, Dict, List

from app.tools.base import ToolSpec
from app.graphs.retrievers import keyword_retriever


def _coerce_int(value: Any, default: int) -> int:
    try:
        v = int(value)
        return v
    except Exception:
        return default


def _search_handler(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Local search tool (no network, no heavy deps).

    Args:
    - query: str (required)
    - top_k: int (optional, default=3)
    Returns:
    - {"query": str, "top_k": int, "docs": [{"doc_id": str, "content": str, ...}, ...]}
    """
    query = args.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("search_tool: args.query must be a non-empty string")

    top_k = _coerce_int(args.get("top_k", 3), default=3)
    if top_k <= 0:
        top_k = 3
    if top_k > 10:
        top_k = 10  # keep output bounded and JSON-safe

    docs: List[Dict[str, Any]] = keyword_retriever(query=query, top_k=top_k)  # type: ignore[arg-type]

    # Ensure JSON-safe shape (best-effort)
    safe_docs: List[Dict[str, Any]] = []
    for d in docs or []:
        if not isinstance(d, dict):
            continue
        doc_id = d.get("doc_id")
        content = d.get("content")
        if not isinstance(doc_id, str):
            doc_id = str(doc_id)
        if not isinstance(content, str):
            content = str(content)
        safe_docs.append({"doc_id": doc_id, "content": content})

    return {"query": query, "top_k": top_k, "docs": safe_docs}


SEARCH_TOOL = ToolSpec(
    name="search_tool",
    description="Local keyword search over a small built-in corpus (no network).",
    args_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query string"},
            "top_k": {"type": "integer", "description": "Number of docs to return (1-10)", "default": 3},
        },
        "required": ["query"],
        "additionalProperties": False,
    },
    handler=_search_handler,
)
