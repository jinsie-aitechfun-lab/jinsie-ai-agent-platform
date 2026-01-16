"""
PCL - Tool 模式（工具协议）

职责：
- 规范工具调用：参数、限制、格式
- 让“工具调用”从口头指令变成工程协议（可校验）
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ToolSpec:
    tool_name: str
    params_desc: Dict[str, str]


def build_tool_prompt(spec: ToolSpec) -> str:
    if spec.params_desc:
        params = "\n".join([f"- {k}：{v}" for k, v in spec.params_desc.items()])
    else:
        params = "（无参数）"
    return (
        f"工具：{spec.tool_name}\n"
        "请严格按参数说明生成工具调用参数。\n"
        "输出必须是 JSON 对象（仅参数对象，不要解释）。\n"
        f"参数说明：\n{params}"
    )
