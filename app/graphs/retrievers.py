"""
Retrievers (Strategy Functions)

这里放“可替换检索策略”。
原则：
- 输入：query: str
- 输出：docs: list[dict]，每项至少有 doc_id / content
- 不依赖网络，不引入重依赖（Skeleton -> 可演进）
"""

from typing import Any, Dict, List


def _mini_corpus() -> List[Dict[str, str]]:
    """
    最小语料库（可替换）。
    目标：让检索从 stub 进入“真实但安全”的阶段。
    """
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


def keyword_retriever(query: str, top_k: int = 2) -> List[Dict[str, Any]]:
    """
    极简关键字检索：
    - 用 query 的字符片段做匹配计分
    - 返回 top_k 条 doc
    """
    query = (query or "").strip()
    corpus = _mini_corpus()

    if not query:
        return corpus[:top_k]

    def score(text: str) -> int:
        # 非严格分词：按字符命中计数（足够用于 Step 12）
        hits = 0
        for ch in query:
            if ch.strip() and ch in text:
                hits += 1
        return hits

    ranked = sorted(corpus, key=lambda d: score(d["content"]), reverse=True)
    return ranked[:top_k]
