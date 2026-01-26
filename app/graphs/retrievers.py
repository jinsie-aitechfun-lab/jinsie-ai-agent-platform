"""
Retrievers (Engineering Stable Version)

目标：
- keyword_retriever：零依赖本地召回（开发/调试阶段使用）
- vector_retriever：Embedding 语义召回（RAG 正式版）

统一协议：
return: List[Dict[str, Any]]
{
    "doc_id": str,
    "content": str,
    "score": float
}
"""

from typing import Any, Dict, List, Tuple
from math import sqrt

# ============================================================
# Mini corpus（本地安全语料）
# ============================================================

def _mini_corpus() -> List[Dict[str, str]]:
    return [
        {
            "doc_id": "note_1",
            "content": "今天完成了 workflow skeleton：Input -> Retrieval -> Reasoning -> Output，且每个节点可插拔。",
        },
        {
            "doc_id": "note_2",
            "content": "retriever/reasoner/renderer 都通过注入策略实现解耦，run 保持稳定，变化集中在策略函数。",
        },
        {
            "doc_id": "note_3",
            "content": "当前阶段不接 LLM、不接向量库，先保证数据协议、可追踪、可回滚、可调试。",
        },
    ]


# ============================================================
# Keyword Retriever（零依赖版）
# ============================================================

def keyword_retriever(query: str, top_k: int = 2) -> List[Dict[str, Any]]:
    query = (query or "").strip()
    corpus = _mini_corpus()

    if not query:
        return [
            {"doc_id": d["doc_id"], "content": d["content"], "score": 1.0}
            for d in corpus[:top_k]
        ]

    def score_text(text: str) -> float:
        hits = sum(1 for ch in query if ch.strip() and ch in text)
        denom = max(1, len([c for c in query if c.strip()]))
        return hits / denom

    ranked = sorted(corpus, key=lambda d: score_text(d["content"]), reverse=True)

    return [
        {
            "doc_id": d["doc_id"],
            "content": d["content"],
            "score": score_text(d["content"]),
        }
        for d in ranked[: max(1, top_k)]
    ]


# ============================================================
# Vector Retriever（Embedding 语义召回）
# ============================================================

def _dot(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _norm(a: List[float]) -> float:
    return sqrt(_dot(a, a))


def _cosine(a: List[float], b: List[float]) -> float:
    na = _norm(a)
    nb = _norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return _dot(a, b) / (na * nb)


def vector_retriever(
    *,
    query: str,
    chunks: List[str],
    embedding_model: str,
    api_key: str,
    base_url: str | None = None,
    top_k: int = 3,
) -> List[Dict[str, Any]]:

    if not chunks:
        return []

    from openai import OpenAI  # 延迟导入，避免 keyword 模式被依赖拖慢

    client = OpenAI(api_key=api_key, base_url=base_url)

    resp = client.embeddings.create(model=embedding_model, input=chunks)
    vecs = [d.embedding for d in resp.data]

    q_vec = client.embeddings.create(model=embedding_model, input=[query]).data[0].embedding

    scored: List[Tuple[float, int]] = [
        (_cosine(q_vec, v), i) for i, v in enumerate(vecs)
    ]
    scored.sort(key=lambda x: x[0], reverse=True)

    return [
        {
            "doc_id": f"chunk_{idx + 1}",
            "content": chunks[idx],
            "score": score,
        }
        for score, idx in scored[: max(1, top_k)]
    ]
