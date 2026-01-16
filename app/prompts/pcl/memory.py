"""
PCL - Memory 模式（记忆协议）

职责：
- 约束可写入/可读取的记忆类型与粒度
- 明确隐私边界：不记录敏感信息
"""
from __future__ import annotations


def build_memory_prompt(*, policy: str = "只记录稳定偏好与长期事实，不记录敏感信息") -> str:
    return (
        "记忆协议：\n"
        f"- 原则：{policy}\n"
        "- 只有在用户明确要求“记住/保存”时才写入。\n"
        "- 内容要短、可验证、可长期复用。"
    )
