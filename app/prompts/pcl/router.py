"""
PCL - Router 模式（路由/分支选择）

职责：
- 在多个工具/策略/分支之间做可解释、可复现的选择
- 通常输出：选择结果 + 简短理由（后续可结构化）
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class RouteOption:
    name: str
    description: str


def build_router_prompt(*, options: List[RouteOption]) -> str:
    lines = ["请在以下选项中选择最合适的一个，并给出一句话理由："]
    for opt in options:
        lines.append(f"- {opt.name}：{opt.description}")
    return "\n".join(lines)
