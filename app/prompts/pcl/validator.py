"""
PCL - Validator 模式（校验/修复）

职责：
- 当输出不符合 schema / 契约时，给出“修复指令”
- 约束修复后的输出仍需严格可解析
"""
from __future__ import annotations


def build_validator_prompt(*, error_summary: str) -> str:
    return (
        "你的上一轮输出未通过校验，需要修复。\n"
        f"校验错误：{error_summary}\n"
        "请按要求修复，并只返回【严格合法 JSON】。不得添加解释文字。"
    )
