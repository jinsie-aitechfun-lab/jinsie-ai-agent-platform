"""
Minimal Workflow Runner ( Skeleton)

目标：
- 把 InputNode -> RetrievalNode 串起来跑通
- 不引入任何复杂框架
- 只验证数据协议与结构
"""

from typing import Any, Dict, List, Optional
import json
from app.graphs.retrievers import keyword_retriever
from app.graphs.reasoners import rule_based_reasoner

from app.graphs.workflow_nodes import InputNode, RetrievalNode, ReasoningNode, OutputNode


def _pretty(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except TypeError:
        return str(obj)


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


def run_minimal_workflow(raw_input: str, trace: bool = False) -> Dict[str, Any]:
    """
    最小工作流：
    raw_input -> InputNode -> RetrievalNode -> output dict
    """
    input_node = InputNode(name="input")
    retrieval_node = RetrievalNode(name="retrieval", retriever=keyword_retriever)
    reasoning_node = ReasoningNode(name="reasoning", reasoner=rule_based_reasoner)
    output_node = OutputNode(name="output")

    nodes = [input_node, retrieval_node, reasoning_node, output_node]
    data: Dict[str, Any] = {"raw_input": raw_input}

    return run_nodes(nodes, data, trace=trace)


if __name__ == "__main__":
    result = run_minimal_workflow("帮我总结一下今天我做了什么", trace=True)

    print("\n=== FINAL OUTPUT ===")
    print(_pretty(result))
