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

    Step 14 目标：
    - 不接 LLM
    - 优先使用 plan（结构化推理结果）来渲染 answer
    - 保持可插拔 renderer
    - 不破坏已有字段，只新增/覆盖 answer
    """

    def __init__(self, name: str, renderer=None):
        super().__init__(name=name)
        self.renderer = renderer or self._stub_renderer

    def _stub_renderer(self, data: Dict[str, Any]) -> str:
        query = data.get("query", "")
        plan = data.get("plan", {})
        docs = data.get("docs", [])

        task_type = plan.get("task_type", "other")
        docs_count = plan.get("docs_count", len(docs))
        next_action = plan.get("next_action", "unknown")
        outline = plan.get("outline", [])

        # 把 docs 做成“要点列表”（更像真实输出，而非 doc_id 拼接）
        doc_bullets = []
        for d in docs:
            content = d.get("content", "")
            if content:
                doc_bullets.append(f"- {content}")
        doc_block = "\n".join(doc_bullets) if doc_bullets else "- (no docs)"

        outline_block = "\n".join([f"- {x}" for x in outline]) if outline else "- (no outline)"

        answer = (
            f"[stub answer]\n"
            f"## 任务\n"
            f"- query: {query}\n"
            f"- task_type: {task_type}\n"
            f"- docs_count: {docs_count}\n"
            f"- next_action: {next_action}\n\n"
            f"## 依据（docs）\n"
            f"{doc_block}\n\n"
            f"## 计划（outline）\n"
            f"{outline_block}\n\n"
            f"Next step would generate a natural language answer with an LLM."
        )
        return answer

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data["answer"] = self.renderer(data)
        return data
