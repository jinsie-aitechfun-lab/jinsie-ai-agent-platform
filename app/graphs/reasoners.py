"""
Reasoners (Strategy Functions)

这里放“可替换推理策略”。
Skeleton -> 真实但安全：不接 LLM，只做规则推理与结构化计划输出。
"""

from typing import Any, Dict, List


def rule_based_reasoner(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    输入：workflow data（至少包含 query / docs）
    输出：一个结构化 plan（dict），用于后续渲染或执行

    规则（非常简单但真实）：
    - 根据 query 判断任务类型（summary / qa / other）
    - 统计 docs 数量
    - 给出下一步动作建议（next_action）
    """
    query = (data.get("query") or "").strip()
    docs: List[Dict[str, Any]] = data.get("docs") or []

    q_lower = query.lower()

    # 任务类型判定（中文也做最小支持）
    if ("总结" in query) or ("概括" in query) or ("sum" in q_lower) or ("summary" in q_lower):
        task_type = "summary"
    elif ("为什么" in query) or ("怎么" in query) or ("what" in q_lower) or ("why" in q_lower) or ("how" in q_lower):
        task_type = "qa"
    else:
        task_type = "other"

    docs_count = len(docs)

    # 下一步动作建议（此处是“推理输出”，不是最终 answer）
    if docs_count == 0:
        next_action = "need_retrieval"
    elif task_type == "summary":
        next_action = "synthesize_summary"
    elif task_type == "qa":
        next_action = "compose_answer"
    else:
        next_action = "clarify_or_answer"

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
