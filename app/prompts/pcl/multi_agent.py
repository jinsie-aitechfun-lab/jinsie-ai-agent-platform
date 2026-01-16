"""
PCL - Multi-Agent 模式（多智能体协作协议）

职责：
- 定义多角色协作：角色职责、消息格式、冲突解决
- 统一输出口径，便于编排与审计
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class AgentRole:
    name: str
    responsibilities: str


def build_multi_agent_prompt(*, roles: List[AgentRole]) -> str:
    lines = ["多智能体协作协议：", "角色定义："]
    for r in roles:
        lines.append(f"- {r.name}：{r.responsibilities}")
    lines.append("规则：消息简洁；冲突显式说明；最终输出必须统一口径。")
    return "\n".join(lines)
