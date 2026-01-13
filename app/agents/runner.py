from __future__ import annotations
from app.agents.plan_executor import execute_plan

import json
from pathlib import Path
from typing import Any, Dict, Optional

from app.services.chat_completion_service import ChatCompletionService
from app.agents.plan_validator import validate_plan_payload



def load_text(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {p.resolve()}")
    return p.read_text(encoding="utf-8")


def validate_payload(payload: dict) -> None:
    """
    Validate payload against the single source of truth:
    app.agents.plan_validator.validate_plan_payload

    This runner keeps validate_payload() as a thin wrapper to avoid
    duplicating schema rules here.
    """
    errors = validate_plan_payload(payload)
    if errors:
        joined = "\n".join(f"- {e}" for e in errors)
        raise ValueError(f"plan contract validation failed:\n{joined}")

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
    #finalize_output 先不调用这个函数
    
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

# Always return full payload to keep output contract stable.
    return payload
