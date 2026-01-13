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
    Validate plan payload via the canonical validator.

    Keep this wrapper to minimize runner churn while centralizing
    plan contract rules in app.agents.plan_validator.
    """
    errors = validate_plan_payload(payload)
    if errors:
        raise ValueError("plan contract validation failed: " + "; ".join(errors))


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
    return payload
