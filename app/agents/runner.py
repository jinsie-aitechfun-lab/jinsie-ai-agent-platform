from __future__ import annotations
from app.agents.plan_executor import execute_plan

import json
from pathlib import Path
from typing import Any, Dict, Optional

from app.services.chat_completion_service import ChatCompletionService


def load_text(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {p.resolve()}")
    return p.read_text(encoding="utf-8")


def validate_payload(payload: dict) -> None:
    # ---- top-level checks ----
    required_top = ["task_summary", "steps", "assumptions", "risks"]
    for k in required_top:
        if k not in payload:
            raise ValueError(f"missing top-level field: {k}")

    if not isinstance(payload["task_summary"], str) or not payload["task_summary"].strip():
        raise ValueError("task_summary must be a non-empty string")

    if not isinstance(payload["steps"], list) or len(payload["steps"]) == 0:
        raise ValueError("steps must be a non-empty array")

    if not isinstance(payload["assumptions"], list) or not all(isinstance(x, str) for x in payload["assumptions"]):
        raise ValueError("assumptions must be an array of strings")

    if not isinstance(payload["risks"], list) or not all(isinstance(x, str) for x in payload["risks"]):
        raise ValueError("risks must be an array of strings")

    # ---- steps schema checks (Day3 V1) ----
    required_step_fields = [
        "step_id",
        "title",
        "description",
        "dependencies",
        "deliverable",
        "acceptance",
    ]

    seen_ids = set()
    for i, step in enumerate(payload["steps"]):
        if not isinstance(step, dict):
            raise ValueError(f"steps[{i}] must be an object")

        for k in required_step_fields:
            if k not in step:
                raise ValueError(f"steps[{i}] missing field: {k}")

        if not isinstance(step["step_id"], str) or not step["step_id"].strip():
            raise ValueError(f"steps[{i}].step_id must be a non-empty string")

        if step["step_id"] in seen_ids:
            raise ValueError(f"duplicate step_id: {step['step_id']}")
        seen_ids.add(step["step_id"])

        for k in ["title", "description", "deliverable", "acceptance"]:
            if not isinstance(step[k], str) or not step[k].strip():
                raise ValueError(f"steps[{i}].{k} must be a non-empty string")

        if not isinstance(step["dependencies"], list) or not all(isinstance(x, str) for x in step["dependencies"]):
            raise ValueError(f"steps[{i}].dependencies must be an array of strings")
        
        # tool can be:
        # 1) "echo_tool"
        # 2) {"name": "echo_tool", "args": {...}}
        if "tool" in step:
            tool = step["tool"]
            if not (isinstance(tool, str) or isinstance(tool, dict)):
                raise ValueError(f"steps[{i}].tool must be a string or an object")

        # args can exist either at step-level (when tool is string) or inside tool object
        if "args" in step and not isinstance(step["args"], dict):
            raise ValueError(f"steps[{i}].args must be an object")

        if "tool" in step and isinstance(step["tool"], dict):
            tool_obj = step["tool"]
            if "args" in tool_obj and not isinstance(tool_obj["args"], dict):
                raise ValueError(f"steps[{i}].tool.args must be an object")


def run_agent_once_raw(
    user_input: str,
    *,
    prompt_path: str = "app/prompts/system/agent_system.md",
    temperature: float = 0.2,
    max_tokens: int = 512,
    service: Optional[ChatCompletionService] = None,
) -> str:
    """
    Run a single agent call and return raw text output.
    """
    system_prompt = load_text(prompt_path).strip()

    svc = service or ChatCompletionService()
    raw = svc.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input.strip()},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return (raw or "").strip()


def run_agent_once_json(
    user_input: str,
    *,
    prompt_path: str = "app/prompts/system/agent_system.md",
    temperature: float = 0.2,
    max_tokens: int = 512,
    debug: bool = False,
    service: Optional[ChatCompletionService] = None,
) -> Dict[str, Any]:
    raw = run_agent_once_raw(
        user_input,
        prompt_path=prompt_path,
        temperature=temperature,
        max_tokens=max_tokens,
        service=service,
    )

    # 1) fail-fast: empty output
    if not raw or not raw.strip():
        raise ValueError("Model output is empty. Check API key/base_url/model, or prompt constraints.")

    text = raw.strip()

    # 2) tolerate fenced JSON (```json ... ```)
    if text.startswith("```"):
        # remove leading ```json / ``` and trailing ```
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # 3) best-effort extract JSON object if model adds extra text
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
    else:
        candidate = text

    try:
        payload = json.loads(candidate)
    except json.JSONDecodeError as e:
        # save raw for debugging
        Path("docs-private/_debug").mkdir(parents=True, exist_ok=True)
        Path("docs-private/_debug/last_agent_raw.txt").write_text(raw, encoding="utf-8")

        preview = raw[:200].replace("\n", "\\n")
        raise ValueError(
            f"Model output is not valid JSON: {e}. "
            f"Raw preview: {preview} (full saved to docs-private/_debug/last_agent_raw.txt)"
        ) from e

    validate_payload(payload)
    payload = execute_plan(payload)
    
    def finalize_output(payload: dict, debug: bool) -> dict:
        """
        Decide what to return to the caller.

        - debug=True: always return full payload
        - debug=False:
            - if any step failed -> return full payload
            - if all steps succeeded -> return last tool output
        """
        if debug:
            return payload

        results = payload.get("execution_results")

        if not results or not isinstance(results, list):
            return payload

        # 如果有任何一步失败，返回完整 payload（便于看 error）
        for r in results:
            if not r.get("ok", True):
                return payload

        last = results[-1]
        if not isinstance(last, dict):
            return payload

        out = last.get("output")
        if isinstance(out, dict):
            return out

        return payload

    return finalize_output(payload, debug=debug)

