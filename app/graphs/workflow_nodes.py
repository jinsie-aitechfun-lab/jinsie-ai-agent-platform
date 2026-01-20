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

    Skeleton 阶段目标：
    - 不做真实推理
    - 不改 query / docs
    - 只新增一个 reasoning 字段，证明“中间态”可以被插入工作流
    """

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        输入协议：
        - data: {"query": str, "docs": list[dict], ...}

        输出协议（新增字段）：
        - {"query": str, "docs": list[dict], "reasoning": str, ...}
        """
        query = data.get("query", "")
        docs = data.get("docs", [])

        reasoning = (
            f"[stub reasoning] received query='{query}', docs_count={len(docs)}. "
            "Next step would combine docs into an answer plan."
        )

        # 保持原结构不被破坏：只在原 data 上新增字段（边界清晰）
        data["reasoning"] = reasoning
        return data



class MemoryNode(BaseNode):
    """Workflow 的记忆节点：存储 / 读取上下文"""

    pass


class OutputNode(BaseNode):
    """
    Workflow 的输出节点：生成最终结果（给用户看的 answer）

    Skeleton 阶段目标：
    - 不做真实 LLM 生成
    - 只把 reasoning + docs 组织成一个可读的占位 answer
    - 不破坏已有字段，只新增 answer
    """

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        query = data.get("query", "")
        reasoning = data.get("reasoning", "")
        docs = data.get("docs", [])

        # 占位答案：让系统“可对外展示”
        doc_preview = "; ".join([d.get("doc_id", "unknown") for d in docs])
        answer = (
            f"[stub answer]\n"
            f"- query: {query}\n"
            f"- reasoning: {reasoning}\n"
            f"- docs: {doc_preview}\n"
            f"Next step would generate a natural language answer."
        )

        data["answer"] = answer
        return data
