"""
Reasoners (Strategy Functions)

这里放“可替换推理策略”。
Skeleton -> 真实但安全：不接 LLM，只做规则推理与结构化计划输出。

Contract（输出 plan 永远包含）：
- task_type: "summary" | "qa" | "other"
- docs_count: int
- next_action: "need_retrieval" | "synthesize_summary" | "compose_answer" | "clarify_or_answer"
- outline: list[str]
"""


from __future__ import annotations

from typing import Any, Dict, List, Callable


# 固定枚举（避免下游出现 "answer" 这种漂移值）
_NEXT_ACTION_NEED_RETRIEVAL = "need_retrieval"
_NEXT_ACTION_SYNTHESIZE_SUMMARY = "synthesize_summary"
_NEXT_ACTION_COMPOSE_ANSWER = "compose_answer"
_NEXT_ACTION_CLARIFY_OR_ANSWER = "clarify_or_answer"


def _safe_text(x: Any) -> str:
    if isinstance(x, str):
        return x.strip()
    return ""


def _infer_task_type(query: str) -> str:
    """
    极简任务类型判定（可控、可回滚）：
    - summary：总结/概括/sum/summary
    - qa：为什么/怎么/是什么/核心能力/介绍/说明/what/why/how
    - other：默认
    """
    q = _safe_text(query)
    q_lower = q.lower()

    if ("总结" in q) or ("概括" in q) or ("sum" in q_lower) or ("summary" in q_lower):
        return "summary"

    if (
        ("为什么" in q)
        or ("怎么" in q)
        or ("是什么" in q)
        or ("核心能力" in q)
        or ("介绍" in q)
        or ("说明" in q)
        or ("what" in q_lower)
        or ("why" in q_lower)
        or ("how" in q_lower)
    ):
        return "qa"

    return "other"


def rule_based_reasoner(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    输入：workflow data（至少包含 query / docs）
    输出：结构化 plan（dict），用于后续渲染或执行
    """
    query = _safe_text(data.get("query"))
    docs: List[Dict[str, Any]] = data.get("docs") or []
    docs_count = len(docs)

    task_type = _infer_task_type(query)

    # 下一步动作建议（推理输出，不是最终 answer）
    if docs_count == 0:
        next_action = _NEXT_ACTION_NEED_RETRIEVAL
    elif task_type == "summary":
        next_action = _NEXT_ACTION_SYNTHESIZE_SUMMARY
    elif task_type == "qa":
        next_action = _NEXT_ACTION_COMPOSE_ANSWER
    else:
        next_action = _NEXT_ACTION_CLARIFY_OR_ANSWER

    plan: Dict[str, Any] = {
        "task_type": task_type,
        "docs_count": docs_count,
        "next_action": next_action,
        "outline": [
            "extract key points from docs",
            "organize into a clear structure",
            "produce final answer",
        ],
    }
    return plan


def _build_simple_reasoner() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """
    simple: 当前默认的规则推理（可控、稳定、可回滚）
    """
    return rule_based_reasoner


def _build_cot_reasoner() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """
    cot: 仍然不接 LLM，但输出一个更“步骤化”的 plan（模拟深度研究的结构）
    注意：这里不输出任何“隐私推理过程”，只做可见的结构化步骤建议。
    """

    def _cot(data: Dict[str, Any]) -> Dict[str, Any]:
        base = rule_based_reasoner(data)

        docs_count = int(base.get("docs_count") or 0)
        task_type = _safe_text(base.get("task_type"))

        outline: List[str] = []
        outline.append("restate the question and scope")
        if docs_count == 0:
            outline.append("identify missing context and request retrieval")
        else:
            outline.append("scan retrieved docs and extract candidate facts")
            outline.append("group facts into themes and resolve conflicts")
        if task_type == "qa":
            outline.append("form a direct answer, then add supporting evidence")
        elif task_type == "summary":
            outline.append("write a concise summary and then a structured bullet list")
        else:
            outline.append("clarify intent or provide a best-effort answer")

        # 保持 Contract 字段不变，只替换 outline，并标注 style
        base["outline"] = outline
        base["reasoner_style"] = "cot"
        return base

    return _cot


def build_reasoner(name: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """
    Builder: 统一入口，返回可注入 ReasoningNode 的 reasoner_fn(data)->plan
    """
    n = _safe_text(name).lower() or "simple"
    if n == "simple":
        return _build_simple_reasoner()
    if n == "cot":
        return _build_cot_reasoner()

    raise ValueError(f"Unknown reasoner: {name}. Allowed: simple, cot")
