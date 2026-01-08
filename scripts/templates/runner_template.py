from __future__ import annotations
"""Runner template (single-run execution scaffold)

Purpose:
- Provide a always-runnable starting point for Agent/Tool execution.
- Optimize for clarity and incremental replacement (mock -> real).
- Keep this file framework-agnostic (no LangChain/LangGraph assumptions).

How to use:
1) Copy this file when starting a new runner or CLI entry.
2) Replace the `mock_model_call()` with your real model call.
3) Implement `dispatch_tool()` for tool execution.
4) Keep the control-flow shape stable: input -> model -> branch -> tool -> model -> output.

Notes:
- `response` is treated as a Python dict (NOT JSON). Keys must be strings.
- If your model returns JSON as strings (e.g., function_call.arguments), parse with json.loads().
"""
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional


# -----------------------------
# 1) Data shapes (minimal)
# -----------------------------

@dataclass
class ToolCall:
    """Represents a tool/function call requested by the model."""
    name: str
    arguments_json: str  # model often returns a JSON string here


@dataclass
class ModelResponse:
    """Normalized model response for runner branching."""
    type: str  # "text" | "function_call"
    content: Optional[str] = None
    tool_call: Optional[ToolCall] = None


# -----------------------------
# 2) Template: runner entrypoint
# -----------------------------

def run_once(user_input: str) -> Dict[str, Any]:
    """Single-run execution entry.

    Returns a JSON-safe dict as the final result (easy to print/log/return via API).
    """
    print("[input]", user_input)

    # Step A: call model (mock for now)
    first = mock_model_call(user_input=user_input)

    # Step B: branch by response type
    if first.type == "text":
        # Final output as JSON-safe dict
        return {
            "type": "text",
            "content": first.content or "",
        }

    if first.type == "function_call" and first.tool_call:
        # Step C: execute tool
        tool_result = dispatch_tool(first.tool_call)

        # Step D: call model again with tool result (mock for now)
        second = mock_model_call(user_input=user_input, tool_result=tool_result)

        # Step E: return final output
        if second.type != "text":
            # Keep Day6 simple: we expect the second call to produce final text/JSON.
            raise RuntimeError(f"Expected final text response, got: {second.type}")

        return {
            "type": "text",
            "content": second.content or "",
            "tool_used": first.tool_call.name,
        }

    raise RuntimeError(f"Unknown/invalid response: {first}")


# -----------------------------
# 3) Model-call mock (replace)
# -----------------------------

def mock_model_call(*, user_input: str, tool_result: Optional[Dict[str, Any]] = None) -> ModelResponse:
    """Mock model call.

    Replace this function with your real model API call and normalization.
    """
    if tool_result is None:
        # First turn: decide to call a tool (example)
        return ModelResponse(
            type="function_call",
            tool_call=ToolCall(
                name="echo_tool",
                arguments_json=json.dumps({"text": user_input}, ensure_ascii=False),
            ),
        )

    # Second turn: final answer after tool result
    return ModelResponse(
        type="text",
        content=f"Tool result received: {tool_result}",
    )


# -----------------------------
# 4) Tool dispatch (implement)
# -----------------------------

def dispatch_tool(call: ToolCall) -> Dict[str, Any]:
    """Dispatch and execute tool calls.

    Keep tool results JSON-safe (dict/list/str/int/float/bool/None).
    """
    args = json.loads(call.arguments_json) if call.arguments_json else {}

    if call.name == "echo_tool":
        # Minimal example tool
        text = str(args.get("text", ""))
        return {"echo": text}

    raise ValueError(f"Unknown tool: {call.name}")


# -----------------------------
# 5) CLI / local run
# -----------------------------

if __name__ == "__main__":
    output = run_once("帮我生成一个严格 JSON 示例")
    print("[output]", output)
