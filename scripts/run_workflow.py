from __future__ import annotations

import argparse
import json
from typing import Any, Dict

from app.graphs.workflow_runner import run_minimal_workflow


def _pretty(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except TypeError:
        return str(obj)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run minimal workflow skeleton (Input -> Retrieval -> Reasoning -> Output)."
    )
    parser.add_argument(
        "query",
        nargs="?",
        default="帮我总结一下今天我做了什么",
        help="User input / query text (default: a demo query).",
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Print node-by-node BEFORE/AFTER data snapshots.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full final output as JSON.",
    )
    parser.add_argument(
        "--answer-only",
        action="store_true",
        help="Print only final answer string (no JSON).",
    )
    args = parser.parse_args()

    out: Dict[str, Any] = run_minimal_workflow(args.query, trace=args.trace)

    if args.answer_only:
        print(out.get("answer", ""))
        return 0

    # default behavior: print JSON (keeping CLI convenient in pipelines)
    if args.json or True:
        print(_pretty(out))
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
