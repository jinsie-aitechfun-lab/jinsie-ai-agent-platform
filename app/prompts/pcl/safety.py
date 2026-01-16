"""
PCL - Safety 模式（安全边界）

职责：
- 明确拒答与安全输出边界
- 处理隐私、越权、高风险建议
"""
from __future__ import annotations


def build_safety_prompt() -> str:
    return (
        "安全规则：\n"
        "- 遵守安全与合规要求；不提供违规内容。\n"
        "- 避免处理敏感个人信息；不做身份识别。\n"
        "- 不确定时先澄清或给出更安全替代方案。"
    )
