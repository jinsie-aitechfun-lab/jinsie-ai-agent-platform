"""
Router Node

目标：
- 在 workflow 最前面做一次“条件分流”
- 不引入复杂框架
- 只做协议与边界：决定走 rag_subflow 还是 default flow

约定：
- 输入 data 至少包含 {"raw_input": str}
- RouterNode 不负责构造 nodes，不做重构，只负责选择 runner

策略（极简可控）：
- query 中包含 “总结” => 走 rag_subflow
- 否则 => 走 default flow
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional


class RouterNode:
    def __init__(
        self,
        name: str,
        *,
        rag_runner: Callable[..., Dict[str, Any]],
        default_runner: Callable[..., Dict[str, Any]],
        trace: bool = False,
    ):
        self.name = name
        self.rag_runner = rag_runner
        self.default_runner = default_runner
        self.trace = trace

    def _pick_route(self, query: str) -> str:
        q = (query or "").strip()
        if "总结" in q:
            return "rag"
        return "default"

    def run(
        self,
        data: Dict[str, Any],
        *,
        rag_kwargs: Optional[Dict[str, Any]] = None,
        default_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        raw_input = data.get("raw_input", "")
        if not isinstance(raw_input, str):
            raw_input = str(raw_input)

        route = self._pick_route(raw_input)

        if self.trace:
            print(f"[router] route={route}")

        if route == "rag":
            return self.rag_runner(raw_input, **(rag_kwargs or {}))

        return self.default_runner(raw_input, **(default_kwargs or {}))
