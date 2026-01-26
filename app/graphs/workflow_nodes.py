"""
Workflow Node Skeletons

这是Skeleton 文件。
它的目标不是实现功能，而是让结构“出现”。

每一个 Node 代表 Workflow 中的一个阶段。
现在它们什么都不做，这是刻意的。
"""

from typing import Any, Dict


class BaseNode:
    """
    所有 Workflow Node 的基类。

    现在只定义最基本的结构，不做任何逻辑。
    """

    def __init__(self, name: str):
        self.name = name

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行当前节点的逻辑。
        约定：
        - data: 上一个节点传下来的结构化数据
        - 返回值: 传给下一个节点的结构化数据
        - 不允许在节点中随意改结构
        """
        raise NotImplementedError("This node is a skeleton.")


class InputNode(BaseNode):
    """
    输入节点：负责接收用户原始输入
    """

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        输入协议：
        - data: {"raw_input": str}
        - 输出: {"query": str}
        """
        raw_input = data.get("raw_input", "")
        return {
            "query": raw_input
        }


class RetrievalNode(BaseNode):
    """
    检索节点：根据 query 获取候选文档

    目标：
    - 默认仍用 stub（保证不炸）
    - 允许注入自定义 retriever（未来接 Milvus / OpenSearch / SearxNG）
    - 节点只负责协议与边界，不负责“具体怎么检索”
    """

    def __init__(self, name: str, retriever=None):
        super().__init__(name=name)
        self.retriever = retriever or self._stub_retriever

    def _stub_retriever(self, query: str):
        # 占位检索：先把 query 当作“命中内容”，让下游能跑通
        return [
            {"doc_id": "stub_1", "content": f"[stub doc] {query}"},
            {"doc_id": "stub_2", "content": f"[stub doc2] {query}"},
        ]

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        输入协议：
        - data: {"query": str}

        输出协议：
        - {"query": str, "docs": list[dict]}
        - docs 每一项至少包含:
            - "doc_id": str
            - "content": str
        """
        query = data.get("query", "")

        # 变化点被隔离在 retriever：Node 只负责调用与保证输出结构
        docs = self.retriever(query)

        return {
            "query": query,
            "docs": docs,
        }


class ToolNode(BaseNode):
    """Workflow 的工具节点：调用工具或函数"""

    pass


class ReasoningNode(BaseNode):
    """
    Workflow 的推理节点：做决策、规划、组合

    目标：
    - 不接 LLM
    - 用“可注入 reasoner”产生结构化 plan
    - 不破坏已有字段，只新增 plan
    """

    def __init__(self, name: str, reasoner=None):
        super().__init__(name=name)
        self.reasoner = reasoner or self._stub_reasoner

    def _stub_reasoner(self, data: Dict[str, Any]) -> Dict[str, Any]:
        query = data.get("query", "")
        docs = data.get("docs", [])
        return {
            "task_type": "other",
            "docs_count": len(docs),
            "next_action": "clarify_or_answer",
            "outline": [
                "extract key points from docs",
                "organize into a clear structure",
                "produce final answer",
            ],
            "note": f"[stub] received query='{query}'",
        }

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        plan = self.reasoner(data)
        data["plan"] = plan
        return data


class MemoryNode(BaseNode):
    """Workflow 的记忆节点：存储 / 读取上下文"""

    pass


class OutputNode(BaseNode):
    """
    Workflow 的输出节点：生成最终结果（给用户看的 answer）

    目标：
    - 不接 LLM
    - 优先使用 plan（结构化推理结果）来渲染 answer
    - 保持可插拔 renderer
    - 不破坏已有字段，只新增/覆盖 answer
    """

    def __init__(self, name: str, renderer=None):
        super().__init__(name=name)
        self.renderer = renderer or self._default_renderer

    def _safe_text(self, s: Any) -> str:
        if isinstance(s, str):
            return s.strip()
        return ""

    def _safe_doc_id(self, d: Any) -> str:
        if isinstance(d, dict):
            v = d.get("doc_id", "")
            if isinstance(v, str) and v.strip():
                return v.strip()
        return "unknown"

    def _pick_doc_points(self, docs: list[dict], max_points: int = 3) -> list[str]:
        """
        从 docs 中挑选若干条 content 作为要点（不做复杂 NLP，规则化、可控、可回滚）。
        """
        points: list[str] = []
        for d in docs:
            if len(points) >= max_points:
                break
            content = self._safe_text(d.get("content"))
            if not content:
                continue
            points.append(content)
        return points

    def _format_docs_as_bullets(self, docs: list[dict], max_points: int = 3) -> list[str]:
        """
        关键增强：把 doc_id 打出来，让输出具备“可解释引用”。
        输出形态：- [doc_id] content
        """
        bullets: list[str] = []
        for d in docs:
            if len(bullets) >= max_points:
                break
            doc_id = self._safe_doc_id(d)
            content = self._safe_text(d.get("content"))
            if not content:
                continue
            bullets.append(f"- [{doc_id}] {content}")
        return bullets

    def _default_renderer(self, data: Dict[str, Any]) -> str:
        query = self._safe_text(data.get("query", ""))
        plan = data.get("plan", {}) or {}
        docs = data.get("docs", []) or []

        task_type = self._safe_text(plan.get("task_type", "other")) or "other"
        docs_count = plan.get("docs_count", len(docs))
        next_action = self._safe_text(plan.get("next_action", "unknown")) or "unknown"
        outline = plan.get("outline", []) or []

        # 1) summary：输出 2~3 条要点（更像真实产品输出）
        if task_type == "summary":
            points = self._format_docs_as_bullets(docs, max_points=3)
            if points:
                bullets = "\n".join(points)
                return (
                    f"今天你主要完成了：\n"
                    f"{bullets}"
                )

            return (
                f"我还没拿到可总结的依据（docs 为空）。\n"
                f"- 你的输入：{query}\n"
                f"- 建议：先补充检索/记录，再生成总结。"
            )

        # 2) qa：保守输出（不接 LLM，先把 docs 作为依据呈现）
        if task_type == "qa":
            points = self._format_docs_as_bullets(docs, max_points=3)
            bullets = "\n".join(points) if points else "- (no docs)"
            return (
                f"问题：{query}\n\n"
                f"我目前的依据（docs）：\n"
                f"{bullets}\n\n"
                f"下一步动作：{next_action}"
            )

        # 3) other：沿用结构化输出（但补上 doc_id 引用）
        doc_bullets = self._format_docs_as_bullets(docs, max_points=8)
        doc_block = "\n".join(doc_bullets) if doc_bullets else "- (no docs)"

        outline_block = "\n".join([f"- {self._safe_text(x)}" for x in outline if self._safe_text(x)]) or "- (no outline)"

        return (
            f"## 任务\n"
            f"- query: {query}\n"
            f"- task_type: {task_type}\n"
            f"- docs_count: {docs_count}\n"
            f"- next_action: {next_action}\n\n"
            f"## 依据（docs）\n"
            f"{doc_block}\n\n"
            f"## 计划（outline）\n"
            f"{outline_block}"
        )

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data["answer"] = self.renderer(data)
        return data
