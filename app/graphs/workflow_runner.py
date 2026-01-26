"""
Minimal Workflow Runner ( Skeleton)

目标：
- 把 InputNode -> RetrievalNode 串起来跑通
- 不引入任何复杂框架
- 只验证数据协议与结构
"""

from typing import Any, Dict, Optional
import json
import os
import re
import sys
from pathlib import Path

from app.graphs.retrievers import keyword_retriever, vector_retriever
from app.graphs.reasoners import rule_based_reasoner

from app.graphs.workflow_nodes import InputNode, RetrievalNode, ReasoningNode, OutputNode


def _pretty(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except TypeError:
        return str(obj)


def _required(name: str) -> str:
    v = os.getenv(name)
    if not v:
        print(f"[error] Missing env var: {name}", file=sys.stderr)
        raise SystemExit(2)
    return v


def _read_text(path: str) -> str:
    p = Path(path)
    if not p.exists():
        print(f"[error] File not found: {p.resolve()}", file=sys.stderr)
        raise SystemExit(2)
    return p.read_text(encoding="utf-8")


def _normalize_whitespace(s: str) -> str:
    s2 = s.replace("\r\n", "\n").replace("\r", "\n")
    s2 = re.sub(r"[ \t]+", " ", s2)
    s2 = re.sub(r"\n{3,}", "\n\n", s2)
    return s2.strip()


def _simple_chunk(
    text: str,
    *,
    chunk_size: int = 900,
    chunk_overlap: int = 120,
) -> list[str]:
    """
    Minimal, stable splitter:
    - Normalize whitespace
    - Split by double newlines first, then pack into windows
    - Add overlap by characters (simple + predictable)
    """
    t = _normalize_whitespace(text)
    if not t:
        return []

    blocks = [b.strip() for b in t.split("\n\n") if b.strip()]
    chunks: list[str] = []
    buf = ""

    def flush_buf() -> None:
        nonlocal buf
        b = buf.strip()
        if b:
            chunks.append(b)
        buf = ""

    for b in blocks:
        if not buf:
            buf = b
            continue

        if len(buf) + 2 + len(b) <= chunk_size:
            buf = f"{buf}\n\n{b}"
        else:
            flush_buf()
            buf = b

    flush_buf()

    if chunk_overlap <= 0:
        return chunks

    overlapped: list[str] = []
    for c in chunks:
        if len(c) <= chunk_size:
            overlapped.append(c)
            continue
        start = 0
        while start < len(c):
            end = min(len(c), start + chunk_size)
            overlapped.append(c[start:end].strip())
            if end >= len(c):
                break
            start = max(0, end - chunk_overlap)

    return [x for x in overlapped if x]


def run_nodes(
    nodes,
    data: Dict[str, Any],
    trace: bool = False,
) -> Dict[str, Any]:
    """
    以固定顺序执行一组 nodes。
    trace=True 时打印每个节点执行前后的 data 快照，用于定位问题。
    """
    for idx, node in enumerate(nodes, start=1):
        if trace:
            print(f"\n--- [{idx}] BEFORE {node.name} ({node.__class__.__name__}) ---")
            print(_pretty(data))

        data = node.run(data)

        if trace:
            print(f"\n--- [{idx}] AFTER  {node.name} ({node.__class__.__name__}) ---")
            print(_pretty(data))

    return data


def _build_keyword_retriever(*, top_k: int):
    # keyword_retriever(query: str, top_k: int=2) -> list[dict]
    def _r(query: str):
        return keyword_retriever(query, top_k=top_k)

    return _r


def _build_vector_retriever(
    *,
    doc_path: str,
    top_k: int,
    chunk_size: int,
    chunk_overlap: int,
):
    """
    vector_retriever 是“语义召回”：
    - 先把 doc 切成 chunks
    - 对 chunks 做 embedding
    - 对 query 做 embedding
    - cosine 相似度取 top_k
    """
    api_key = _required("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL")
    if not embedding_model:
        print("[error] Missing env var: OPENAI_EMBEDDING_MODEL", file=sys.stderr)
        raise SystemExit(2)

    raw = _read_text(doc_path)
    chunks = _simple_chunk(raw, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    if not chunks:
        print("[error] Document is empty after normalization/chunking.", file=sys.stderr)
        raise SystemExit(2)

    def _r(query: str):
        return vector_retriever(
            query=query,
            chunks=chunks,
            embedding_model=embedding_model,
            api_key=api_key,
            base_url=base_url,
            top_k=top_k,
        )

    return _r


def run_minimal_workflow(
    raw_input: str,
    *,
    trace: bool = False,
    retriever: str = "keyword",
    doc: Optional[str] = None,
    top_k: int = 3,
    chunk_size: int = 900,
    chunk_overlap: int = 120,
) -> Dict[str, Any]:
    """
    最小工作流：
    raw_input -> InputNode -> RetrievalNode -> ReasoningNode -> OutputNode -> output dict
    """
    input_node = InputNode(name="input")

    if retriever == "vector":
        if not doc:
            print("[error] --doc is required when --retriever=vector", file=sys.stderr)
            raise SystemExit(2)
        retrieval_fn = _build_vector_retriever(
            doc_path=doc,
            top_k=top_k,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    else:
        retrieval_fn = _build_keyword_retriever(top_k=top_k)

    retrieval_node = RetrievalNode(name="retrieval", retriever=retrieval_fn)
    reasoning_node = ReasoningNode(name="reasoning", reasoner=rule_based_reasoner)
    output_node = OutputNode(name="output")

    nodes = [input_node, retrieval_node, reasoning_node, output_node]
    data: Dict[str, Any] = {"raw_input": raw_input}

    return run_nodes(nodes, data, trace=trace)


if __name__ == "__main__":
    result = run_minimal_workflow(
        "帮我总结一下今天我做了什么",
        trace=True,
        retriever="keyword",
        top_k=2,
    )

    print("\n=== FINAL OUTPUT ===")
    print(_pretty(result))
