"""
PCL - System 模式（系统契约）

职责：
- 定义“全局行为契约”：角色、边界、输出风格、禁止项
- 作为所有 prompt 的最高优先级约束

说明：
- 当前是最小骨架，用于让工程可验证（verify_prompt_control_layer.py PASS）
- 具体内容后续在 Workflow Skeleton 阶段逐步增强
"""
from __future__ import annotations


def build_system_prompt(*, product_name: str = "Jinsie AI Agent Platform") -> str:
    return (
        f"你是 {product_name} 的智能体系统。"
        "你必须遵守工程契约：输出可控、可解析、可复现；遇到不确定先澄清；不得编造。"
    )
