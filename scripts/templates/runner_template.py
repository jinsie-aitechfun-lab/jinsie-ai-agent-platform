from __future__ import annotations

"""
Runner 模板（单次执行骨架）

用途：
- 提供一个【始终可运行】的 Agent / Tool 执行起点
- 支持从 mock → 真实模型调用 的渐进式替换
- 保持 runner 结构稳定，不绑定任何特定框架（不假设 LangChain / LangGraph）

使用方式：
1）新建 runner / CLI 入口时，参考或复制此文件
2）用真实模型调用替换 mock_model_call()
3）在 dispatch_tool() 中实现工具执行（tool dispatch）
4）始终保持控制流形态稳定：
   input → model → 分支 → tool → model → output

设计约束（很重要）：
- response 始终当作 Python dict 处理（不是 JSON 字符串）
- dict 的 key 必须是字符串
- 如果模型返回的是 JSON 字符串（如 function_call.arguments），必须用 json.loads() 显式解析
"""

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional


# -----------------------------
# 1) 数据结构（最小闭环）
# -----------------------------

@dataclass
class ToolCall:
    """模型请求执行某个工具（tool/function）时的标准结构。"""
    name: str
    arguments_json: str  # 很多模型会把参数以 JSON 字符串形式返回


@dataclass
class ModelResponse:
    """Runner 内部使用的“归一化响应”，用于分支判断。"""
    type: str  # "text" | "function_call"
    content: Optional[str] = None
    tool_call: Optional[ToolCall] = None


# -----------------------------
# 2) 模板：Runner 单次执行入口
# -----------------------------

def run_once(user_input: str) -> Dict[str, Any]:
    """单次执行入口。

    返回值：必须是 JSON-safe 的 dict（方便 print / log / API return）。
    """
    print("[input]", user_input)

    # Step A：调用模型（当前为 mock，后续替换为真实模型调用）
    first = mock_model_call(user_input=user_input)

    # Step B：根据响应类型分支
    if first.type == "text":
        # 直接返回最终结果（JSON-safe dict）
        return {
            "type": "text",
            "content": first.content or "",
        }

    if first.type == "function_call" and first.tool_call:
        # Step C：执行工具
        tool_result = dispatch_tool(first.tool_call)

        # Step D：把工具结果喂回模型，得到最终输出（当前为 mock）
        second = mock_model_call(user_input=user_input, tool_result=tool_result)

        # Step E：返回最终结果
        if second.type != "text":
            # Minimal contract closure: the second model call must output final text/JSON.
            raise RuntimeError(f"Expected final text response, got: {second.type}")

        return {
            "type": "text",
            "content": second.content or "",
            "tool_used": first.tool_call.name,
        }

    raise RuntimeError(f"Unknown/invalid response: {first}")


# -----------------------------
# 3) 模型调用 mock（后续替换）
# -----------------------------

def mock_model_call(*, user_input: str, tool_result: Optional[Dict[str, Any]] = None) -> ModelResponse:
    """模型调用（mock 版）。

    你要替换的就是这个函数：
    - 用真实模型 API 调用替换 mock
    - 并在这里把原始响应“归一化”为 ModelResponse
    """
    if tool_result is None:
        # 第一轮：示例——模型决定要调用一个工具
        return ModelResponse(
            type="function_call",
            tool_call=ToolCall(
                name="echo_tool",
                arguments_json=json.dumps({"text": user_input}, ensure_ascii=False),
            ),
        )

    # 第二轮：示例——拿到工具结果后，产出最终回复
    return ModelResponse(
        type="text",
        content=f"Tool result received: {tool_result}",
    )


# -----------------------------
# 4) 工具分发与执行（需要实现）
# -----------------------------

def dispatch_tool(call: ToolCall) -> Dict[str, Any]:
    """根据 ToolCall 执行具体工具，并返回 JSON-safe 的结果。

    约束：
    - 工具返回值必须是 JSON-safe：dict/list/str/int/float/bool/None
    - arguments_json 是 JSON 字符串：要用 json.loads() 解析成 dict
    """
    args = json.loads(call.arguments_json) if call.arguments_json else {}

    if call.name == "echo_tool":
        # 最小示例工具：回显输入
        text = str(args.get("text", ""))
        return {"echo": text}

    raise ValueError(f"Unknown tool: {call.name}")


# -----------------------------
# 5) CLI / 本地运行（可选）
# -----------------------------

if __name__ == "__main__":
    output = run_once("帮我生成一个严格 JSON 示例")
    print("[output]", output)
