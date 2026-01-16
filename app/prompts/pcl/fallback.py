"""
PCL - Fallback 模式（失败回退）

职责：
- 当工具失败/信息不足/解析失败时，统一回退策略
- 禁止编造，优先最小澄清问题
"""
from __future__ import annotations


def build_fallback_prompt(*, reason: str) -> str:
    return (
        "触发失败回退策略。\n"
        f"原因：{reason}\n"
        "要求：不得编造；如缺少关键信息，提出最小澄清问题；否则给出安全的降级输出。"
    )
