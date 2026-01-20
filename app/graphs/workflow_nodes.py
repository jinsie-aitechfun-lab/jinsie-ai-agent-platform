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
    - 默认仍用 stub reasoner（保证不炸）
    - 允许注入自定义 reasoner（未来接真实 Planner / LLM 推理 / 规则引擎）
    - Node 只负责协议与边界，不负责“具体怎么推理”
    """

    def __init__(self, name: str, reasoner=None):
        super().__init__(name=name)
        self.reasoner = reasoner or self._stub_reasoner

    def _stub_reasoner(self, query: str, docs):
        return (
            f"[stub reasoning] received query='{query}', docs_count={len(docs)}. "
            "Next step would combine docs into an answer plan."
        )

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        输入协议：
        - data: {"query": str, "docs": list[dict], ...}

        输出协议（新增字段）：
        - {"query": str, "docs": list[dict], "reasoning": str, ...}
        """
        query = data.get("query", "")
        docs = data.get("docs", [])

        # 变化点被隔离在 reasoner：Node 只负责调用与保证输出结构
        reasoning = self.reasoner(query, docs)

        data["reasoning"] = reasoning
        return data


class MemoryNode(BaseNode):
    """Workflow 的记忆节点：存储 / 读取上下文"""

    pass


class OutputNode(BaseNode):
    """
    Workflow 的输出节点：生成最终结果（给用户看的 answer）

    目标：
    - 默认仍用 stub renderer（保证不炸）
    - 允许注入自定义 renderer（未来接 LLM / 模板渲染 / 多格式输出）
    - Node 只负责协议与边界，不负责“具体怎么生成 answer”
    """

    def __init__(self, name: str, renderer=None):
        super().__init__(name=name)
        self.renderer = renderer or self._stub_renderer

    def _stub_renderer(self, query: str, reasoning: str, docs):
        doc_preview = "; ".join([d.get("doc_id", "unknown") for d in docs])
        return (
            f"[stub answer]\n"
            f"- query: {query}\n"
            f"- reasoning: {reasoning}\n"
            f"- docs: {doc_preview}\n"
            f"Next step would generate a natural language answer."
        )

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        输入协议：
        - data: {"query": str, "docs": list[dict], "reasoning": str, ...}

        输出协议（新增字段）：
        - {"answer": str, ...}  且不破坏已有字段
        """
        query = data.get("query", "")
        reasoning = data.get("reasoning", "")
        docs = data.get("docs", [])

        # 变化点被隔离在 renderer：Node 只负责调用与保证输出结构
        answer = self.renderer(query, reasoning, docs)

        data["answer"] = answer
        return data
