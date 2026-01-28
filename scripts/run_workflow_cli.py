#!/usr/bin/env python3
"""
Workflow CLI Runner

目标：
- 一条命令即可运行 workflow（本地版）
- 为 FastAPI 包装做准备（不涉及云部署）

用法示例：
PYTHONPATH=. python scripts/run_workflow_cli.py "帮我总结今天做了什么" --trace
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, Optional

from app.graphs.workflow_runner import run_minimal_workflow


def _pretty(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except TypeError:
        return str(obj)


def _extract_answer(result: Any) -> Optional[str]:
    """
    尽量“少猜测但可用”：
    - 优先取 result["answer"]
    - 若不存在，尝试一些常见字段，但不强依赖
    - 都没有就返回 None，让上层打印全量 result
    """
    if not isinstance(result, dict):
        return None

    if isinstance(result.get("answer"), str) and result.get("answer"):
        return result["answer"]

    # 保守兜底：不保证存在，仅提高可用性
    for k in ("final_answer", "output", "result", "text", "content"):
        v = result.get(k)
        if isinstance(v, str) and v:
            return v

    return None


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run minimal workflow locally via CLI.")
    p.add_argument("query", help="raw input query string")
    p.add_argument("--trace", action="store_true", help="print router/nodes trace")
    p.add_argument(
        "--retriever",
        choices=["keyword", "vector"],
        default="keyword",
        help="retriever type",
    )
    p.add_argument(
        "--reasoner",
        default="simple",
        help="reasoner type (kept for compatibility; current runner may ignore it)",
    )
    p.add_argument(
        "--doc",
        default=None,
        help="document path for vector retriever (required if --retriever=vector)",
    )
    p.add_argument("--top-k", type=int, default=3, help="top_k for retriever")
    p.add_argument("--chunk-size", type=int, default=900, help="chunk size for vector mode")
    p.add_argument(
        "--chunk-overlap",
        type=int,
        default=120,
        help="chunk overlap for vector mode",
    )
    p.add_argument(
        "--print-json",
        action="store_true",
        help="print full result json (instead of answer only)",
    )
    return p


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)

    result: Dict[str, Any] = run_minimal_workflow(
        args.query,
        trace=args.trace,
        retriever=args.retriever,
        reasoner=args.reasoner,
        doc=args.doc,
        top_k=args.top_k,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    if args.print_json:
        print(_pretty(result))
        return 0

    answer = _extract_answer(result)
    if answer is not None:
        print(answer)
        return 0

    # 不静默：如果找不到 answer，就打印全量，保证 CLI 可用
    print(_pretty(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
