from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from app.graphs.retrievers import vector_retriever
from app.services.chat_completion_service import ChatCompletionService


def _required(name: str) -> str:
    v = os.getenv(name)
    if not v:
        print(f"[error] Missing env var: {name}", file=sys.stderr)
        sys.exit(2)
    return v


def _read_text(path: str) -> str:
    p = Path(path)
    if not p.exists():
        print(f"[error] File not found: {p.resolve()}", file=sys.stderr)
        sys.exit(2)
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
) -> List[str]:
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
    chunks: List[str] = []
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

    # Overlap: create sliding windows if chunks are big; for small chunks keep as-is.
    if chunk_overlap <= 0:
        return chunks

    overlapped: List[str] = []
    for c in chunks:
        if len(c) <= chunk_size:
            overlapped.append(c)
            continue
        # fallback: hard slice with overlap
        start = 0
        while start < len(c):
            end = min(len(c), start + chunk_size)
            overlapped.append(c[start:end].strip())
            if end >= len(c):
                break
            start = max(0, end - chunk_overlap)

    return [x for x in overlapped if x]


def _keyword_retrieve_over_chunks(
    *,
    query: str,
    chunks: List[str],
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    """
    本地关键字检索（不走 embedding、不依赖网络）：
    - 对每个 chunk 做一个非常简单的“命中计分”
    - 返回与 vector_retriever 相同的数据协议：[{doc_id, content, score}]
    """
    if not chunks:
        return []

    q = (query or "").strip()
    if not q:
        # query 为空：直接返回前 top_k
        docs: List[Dict[str, Any]] = []
        for i, t in enumerate(chunks[: max(1, top_k)], start=1):
            docs.append({"doc_id": f"chunk_{i}", "content": t, "score": 0.0})
        return docs

    q_lower = q.lower()

    def score(text: str) -> float:
        t = (text or "").lower()
        # 1) 直接子串命中（很强信号）
        s = 0.0
        if q_lower in t:
            s += 10.0
        # 2) 按“词片段”粗糙计分（足够用于工程骨架）
        tokens = [x for x in re.split(r"[\s\W]+", q_lower) if x]
        for tok in tokens:
            if tok and tok in t:
                s += 2.0
        # 3) 兜底：按字符命中（中文也能用）
        for ch in q:
            if ch.strip() and ch in text:
                s += 0.1
        return s

    scored: List[Tuple[float, int]] = []
    for i, t in enumerate(chunks):
        scored.append((score(t), i))

    scored.sort(key=lambda x: x[0], reverse=True)

    docs: List[Dict[str, Any]] = []
    for s, idx in scored[: max(1, top_k)]:
        docs.append(
            {
                "doc_id": f"chunk_{idx + 1}",
                "content": chunks[idx],
                "score": s,
            }
        )
    return docs


def _build_context_from_docs(
    docs: List[Dict[str, Any]],
    *,
    max_chars: int = 3500,
) -> Tuple[str, List[str]]:
    """
    输入：
      docs: [{doc_id, content, score}]
    输出：
      context_text: 拼接后的上下文（带 doc_id + score）
      source_ids: 参与拼接的 doc_id 列表
    """
    parts: List[str] = []
    source_ids: List[str] = []
    used = 0

    for d in docs:
        doc_id = str(d.get("doc_id", "unknown"))
        content = str(d.get("content", ""))
        score = d.get("score", None)

        if score is None:
            header = f"[{doc_id}]\n"
        else:
            try:
                header = f"[{doc_id} | score={float(score):.3f}]\n"
            except Exception:
                header = f"[{doc_id}]\n"

        block = f"{header}{content}\n"
        if used + len(block) > max_chars and parts:
            break

        parts.append(block)
        source_ids.append(doc_id)
        used += len(block)

    return "\n---\n".join(parts).strip(), source_ids


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a minimal RAG demo (local doc -> chunks -> retrieve -> answer with citations)."
    )
    parser.add_argument("question", type=str, help="User question")
    parser.add_argument(
        "--doc",
        type=str,
        default="docs/samples/rag_seed.md",
        help="Path to a local markdown/text file",
    )
    parser.add_argument(
        "--retriever",
        type=str,
        choices=["vector", "keyword"],
        default="vector",
        help="Retriever strategy: vector (embeddings) or keyword (local, no embeddings).",
    )
    parser.add_argument("--top-k", type=int, default=3, help="How many chunks to retrieve")
    parser.add_argument("--chunk-size", type=int, default=900, help="Chunk size (chars)")
    parser.add_argument("--chunk-overlap", type=int, default=120, help="Chunk overlap (chars)")
    parser.add_argument("--max-context-chars", type=int, default=3500, help="Max context chars fed to LLM")
    parser.add_argument("--temperature", type=float, default=0.2, help="LLM temperature")
    parser.add_argument("--max-tokens", type=int, default=600, help="LLM max tokens")
    args = parser.parse_args()

    # ---- env (reuse your existing conventions) ----
    api_key = _required("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    # embedding_model 仅在 vector 模式下强制需要
    embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL")
    if args.retriever == "vector" and not embedding_model:
        print("[error] Missing env var: OPENAI_EMBEDDING_MODEL", file=sys.stderr)
        sys.exit(2)

    # ---- load + chunk ----
    raw = _read_text(args.doc)
    chunks_text = _simple_chunk(raw, chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
    if not chunks_text:
        print("[error] Document is empty after normalization/chunking.", file=sys.stderr)
        sys.exit(2)

    # ---- retrieve (pluggable strategy) ----
    if args.retriever == "keyword":
        docs = _keyword_retrieve_over_chunks(
            query=args.question,
            chunks=chunks_text,
            top_k=args.top_k,
        )
    else:
        docs = vector_retriever(
            query=args.question,
            chunks=chunks_text,
            embedding_model=str(embedding_model),
            api_key=api_key,
            base_url=base_url,
            top_k=args.top_k,
        )

    context_text, source_ids = _build_context_from_docs(docs, max_chars=args.max_context_chars)

    # ---- ask LLM (reuse your ChatCompletionService) ----
    chat = ChatCompletionService(api_key=api_key, base_url=base_url)

    system = (
        "You are a helpful assistant. Answer using ONLY the provided CONTEXT. "
        "If the answer is not in the context, say you don't know. "
        "Cite sources by doc_id in the form [chunk_1]."
    )
    user = f"QUESTION:\n{args.question}\n\nCONTEXT:\n{context_text}\n"

    answer = chat.create(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    ).strip()

    print("\n=== Answer ===")
    print(answer or "(empty)")
    print("\n=== Sources ===")
    if source_ids:
        for cid in source_ids:
            print(f"- {cid}")
    else:
        print("- (none)")


if __name__ == "__main__":
    main()
