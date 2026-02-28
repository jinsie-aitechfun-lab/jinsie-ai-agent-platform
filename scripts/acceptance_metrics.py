#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Day34 Acceptance Script (local engineering guardrail)

Verifies (repeatable):
1) /v1/workflow/run keyword:
   - print metrics.total_ms / retrieval_ms / llm_ms
   - assert retrieval_ms > 0
2) run_minimal_workflow vector:
   - run once with docs/samples/rag_seed.md (seed)
   - assert retrieval_ms > 0

Constraints:
- no contract change
- no runner change
- no new deps
- no README change
- no logging framework
- only 1 script file (this file)
"""

from __future__ import annotations

import argparse
import inspect
import json
import sys
import time
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Iterable, Tuple
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
import importlib.util


RE_DEF_RUN_MINIMAL = re.compile(r"^\s*def\s+run_minimal_workflow\s*\(", re.M)
RE_METRICS_KEYS = ("metrics", "metric", "timing", "latency")


@dataclass
class Metrics:
    total_ms: float
    retrieval_ms: float
    llm_ms: float

    @staticmethod
    def from_any(obj: Any) -> "Metrics":
        """
        Strict-ish parse: require retrieval_ms.
        total_ms/llm_ms may be absent in some runner outputs; caller can patch them.
        """
        if obj is None:
            raise ValueError("empty response object")

        if isinstance(obj, Metrics):
            return obj

        if not isinstance(obj, dict):
            raise ValueError(f"metrics extraction expects dict, got: {type(obj)}")

        # 1) Standard: {"metrics": {...}}
        m = _find_metrics_dict(obj)
        if m is not None:
            return Metrics(
                total_ms=float(m.get("total_ms", 0.0) or 0.0),
                retrieval_ms=float(m.get("retrieval_ms", 0.0) or 0.0),
                llm_ms=float(m.get("llm_ms", 0.0) or 0.0),
            )

        # 2) Look for flat keys anywhere
        retrieval_ms = _deep_find_first_number_by_keys(
            obj,
            keys=(
                ("retrieval_ms",),
                ("retrieval_time_ms",),
                ("timings", "retrieval_ms"),
                ("timing", "retrieval_ms"),
                ("latency", "retrieval_ms"),
                ("retrieval", "retrieval_ms"),
                ("retrieval", "ms"),
                ("retrieval", "duration_ms"),
            ),
        )

        if retrieval_ms is None:
            raise ValueError("cannot find metrics{total_ms,retrieval_ms,llm_ms} in response")

        total_ms = _deep_find_first_number_by_keys(
            obj,
            keys=(
                ("total_ms",),
                ("timings", "total_ms"),
                ("timing", "total_ms"),
                ("latency", "total_ms"),
                ("duration_ms",),
            ),
        )

        llm_ms = _deep_find_first_number_by_keys(
            obj,
            keys=(
                ("llm_ms",),
                ("timings", "llm_ms"),
                ("timing", "llm_ms"),
                ("latency", "llm_ms"),
                ("llm", "llm_ms"),
                ("llm", "ms"),
                ("llm", "duration_ms"),
            ),
        )

        return Metrics(
            total_ms=float(total_ms or 0.0),
            retrieval_ms=float(retrieval_ms),
            llm_ms=float(llm_ms or 0.0),
        )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_json(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))


def _http_post_json(url: str, payload: Dict[str, Any], timeout_s: int = 30) -> Dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(
        url=url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except HTTPError as e:
        raw = ""
        try:
            raw = e.read().decode("utf-8")
        except Exception:
            pass
        raise RuntimeError(f"HTTP {e.code} {e.reason}: {raw}") from e
    except URLError as e:
        raise RuntimeError(f"URL error: {e}") from e


def _find_metrics_dict(obj: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if "metrics" in obj and isinstance(obj["metrics"], dict):
        return obj["metrics"]
    for k in ("answer", "output", "result", "data"):
        if k in obj and isinstance(obj[k], dict) and "metrics" in obj[k] and isinstance(obj[k]["metrics"], dict):
            return obj[k]["metrics"]
    for k in RE_METRICS_KEYS:
        if k in obj and isinstance(obj[k], dict):
            cand = obj[k]
            if all(x in cand for x in ("total_ms", "retrieval_ms", "llm_ms")):
                return cand
    return None


def _deep_find_first_number_by_keys(obj: Any, keys: Iterable[Tuple[str, ...]]) -> Optional[float]:
    """
    Try a list of key-path candidates; return the first numeric value found.
    Example key path: ("timings","retrieval_ms") means obj["timings"]["retrieval_ms"].
    Also supports scanning dict/list recursively for a terminal key (single-element path).
    """
    # direct path try
    for path in keys:
        v = _get_by_path(obj, path)
        n = _to_number(v)
        if n is not None:
            return n

    # fallback: if any single terminal key appears deeply, pick first numeric
    terminals = {p[0] for p in keys if len(p) == 1}
    if terminals:
        found = _deep_find_first(obj, lambda d: any(k in d for k in terminals))
        if found is not None:
            for k in terminals:
                if k in found:
                    n = _to_number(found.get(k))
                    if n is not None:
                        return n
    return None


def _get_by_path(obj: Any, path: Tuple[str, ...]) -> Any:
    cur = obj
    for k in path:
        if not isinstance(cur, dict):
            return None
        if k not in cur:
            return None
        cur = cur[k]
    return cur


def _to_number(v: Any) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            return None
    return None


def _deep_find_first(obj: Any, pred) -> Optional[Dict[str, Any]]:
    if isinstance(obj, dict):
        if pred(obj):
            return obj
        for v in obj.values():
            r = _deep_find_first(v, pred)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for it in obj:
            r = _deep_find_first(it, pred)
            if r is not None:
                return r
    return None


def _print_metrics(label: str, m: Metrics) -> None:
    print(f"\n== {label} metrics ==")
    print(f"total_ms:     {m.total_ms}")
    print(f"retrieval_ms: {m.retrieval_ms}")
    print(f"llm_ms:       {m.llm_ms}")


def _assert_retrieval_positive(label: str, m: Metrics) -> None:
    if not (m.retrieval_ms and m.retrieval_ms > 0):
        raise AssertionError(f"[{label}] expected retrieval_ms > 0, got: {m.retrieval_ms}")


def _auto_pick_keyword_request(repo: Path) -> Optional[Path]:
    candidates = []
    for p in repo.rglob("*.json"):
        sp = str(p).lower()
        if "/.venv/" in sp or "/.git/" in sp:
            continue
        if "docs" not in sp:
            continue
        if "sample" not in sp and "samples" not in sp:
            continue
        if "workflow" in sp or "v1" in sp or "run" in sp:
            candidates.append(p)

    candidates.sort(key=lambda x: str(x))
    return candidates[0] if candidates else None


def _minimal_keyword_payload() -> Dict[str, Any]:
    """
    Minimal best-effort payload for /v1/workflow/run keyword case.

    Contract signal from server (FastAPI 422):
    - body.input is required
    - body.input must be a string
    """
    return {"input": "Acceptance keyword run: summarize intro in 3 bullet points."}


def _case1_workflow_keyword(base_url: str, keyword_req: Optional[Path], timeout_s: int) -> Metrics:
    repo = _repo_root()

    payload: Dict[str, Any]
    used_req: str

    if keyword_req is not None:
        if not keyword_req.exists():
            raise RuntimeError(f"--keyword-req not found: {keyword_req}")
        payload = _load_json(keyword_req)
        used_req = str(keyword_req)
    else:
        picked = _auto_pick_keyword_request(repo)
        if picked is not None:
            payload = _load_json(picked)
            used_req = str(picked)
        else:
            payload = _minimal_keyword_payload()
            used_req = "<inline minimal payload>"

    url = base_url.rstrip("/") + "/v1/workflow/run"

    print("== Case1 /v1/workflow/run keyword ==")
    print(f"base_url: {base_url}")
    print(f"request:  {used_req}")
    print(f"payload_keys: {sorted(list(payload.keys()))}")

    t0 = time.time()
    resp = _http_post_json(url, payload, timeout_s=timeout_s)
    dt = (time.time() - t0) * 1000.0
    print(f"http_total_ms(observed): {dt:.2f}")

    m = Metrics.from_any(resp)
    _print_metrics("Case1(keyword)", m)
    _assert_retrieval_positive("Case1(keyword)", m)
    return m


def _find_run_minimal_workflow_py(repo: Path) -> Optional[Path]:
    for p in repo.rglob("*.py"):
        sp = str(p)
        if "/.venv/" in sp or "/.git/" in sp:
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if RE_DEF_RUN_MINIMAL.search(txt):
            return p
    return None


def _load_module_from_file(py_file: Path, module_name: str = "_acceptance_minimal_workflow") -> Any:
    spec = importlib.util.spec_from_file_location(module_name, str(py_file))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module spec from: {py_file}")
    mod = importlib.util.module_from_spec(spec)
    repo = _repo_root()
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    spec.loader.exec_module(mod)
    return mod


def _call_run_minimal_workflow(func, seed_path: Path) -> Dict[str, Any]:
    """
    Deterministic call for your actual signature:
      run_minimal_workflow(raw_input: str, *, retriever: str="keyword", doc: Optional[str]=None, ...)
    """
    sig = inspect.signature(func)
    kwargs: Dict[str, Any] = {}

    # required
    if "raw_input" in sig.parameters:
        kwargs["raw_input"] = "Please answer based on the provided doc. Give 3 bullet points."  # no '总结' to avoid rag_subflow

    # force vector + doc
    if "retriever" in sig.parameters:
        kwargs["retriever"] = "vector"
    if "doc" in sig.parameters:
        kwargs["doc"] = str(seed_path)

    # conservative optionals
    if "trace" in sig.parameters:
        kwargs["trace"] = False
    if "top_k" in sig.parameters:
        kwargs["top_k"] = 3

    out = func(**kwargs)

    if out is None:
        return {}
    if isinstance(out, dict):
        return out
    if hasattr(out, "dict") and callable(getattr(out, "dict")):
        try:
            return out.dict()
        except Exception:
            pass
    return {"result": out}


def _case2_minimal_workflow_vector(seed_path: Path) -> Metrics:
    repo = _repo_root()
    py_file = _find_run_minimal_workflow_py(repo)
    if py_file is None:
        raise RuntimeError("Cannot find 'def run_minimal_workflow(' in repo.")

    print("\n== Case2 run_minimal_workflow vector ==")
    print(f"entry_py: {py_file}")
    print(f"seed_md:  {seed_path}")

    mod = _load_module_from_file(py_file)
    if not hasattr(mod, "run_minimal_workflow"):
        raise RuntimeError(f"Found file but no symbol run_minimal_workflow in: {py_file}")

    func = getattr(mod, "run_minimal_workflow")
    t0 = time.time()
    resp = _call_run_minimal_workflow(func, seed_path=seed_path)
    dt_ms = (time.time() - t0) * 1000.0
    print(f"py_total_ms(observed): {dt_ms:.2f}")

    # Debug help (no logging framework): print top-level keys only
    if isinstance(resp, dict):
        print(f"resp_keys: {sorted(list(resp.keys()))}")

    # Parse metrics; if total_ms missing, patch with observed dt
    m = Metrics.from_any(resp)
    if not (m.total_ms and m.total_ms > 0):
        m = Metrics(total_ms=float(dt_ms), retrieval_ms=m.retrieval_ms, llm_ms=m.llm_ms)

    _print_metrics("Case2(vector)", m)
    _assert_retrieval_positive("Case2(vector)", m)
    return m


def main() -> int:
    repo = _repo_root()

    parser = argparse.ArgumentParser(
        description="Day34 acceptance: make workflow metrics repeatably verifiable (no contract change)."
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="FastAPI base URL")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout seconds")
    parser.add_argument(
        "--keyword-req",
        default="",
        help="Path to JSON request body for /v1/workflow/run (keyword). If empty, use inline minimal payload.",
    )
    parser.add_argument(
        "--seed-md",
        default=str(repo / "docs" / "samples" / "rag_seed.md"),
        help="Seed markdown path for run_minimal_workflow (vector). Default: docs/samples/rag_seed.md",
    )

    args = parser.parse_args()
    keyword_req = Path(args.keyword_req).resolve() if args.keyword_req else None
    seed_md = Path(args.seed_md).resolve()

    if not seed_md.exists():
        raise RuntimeError(f"seed markdown not found: {seed_md}")

    print("=== Day34 acceptance start ===")
    print(f"repo: {repo}")

    _case1_workflow_keyword(args.base_url, keyword_req, timeout_s=args.timeout)
    _case2_minimal_workflow_vector(seed_md)

    print("\n=== Day34 acceptance PASSED ✅ ===")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print("\n=== Day34 acceptance FAILED ❌ ===", file=sys.stderr)
        print(str(e), file=sys.stderr)
        raise