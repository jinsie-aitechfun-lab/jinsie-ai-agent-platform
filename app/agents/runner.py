from __future__ import annotations
# Module: agent_orchestration
# Boundary: do NOT import app.tools/* (tool dispatch is execution_engine/tool_runtime responsibility)
# See: docs/architecture/modules.md
from app.agents.plan_executor import execute_plan

import json
from pathlib import Path
from typing import Any, Dict, Optional, List

from app.services.chat_completion_service import ChatCompletionService
from app.agents.plan_validator import validate_plan_payload

# ✅ PCL schema (minimal wiring, optional)
from app.prompts.pcl.schema import SchemaSpec, build_schema_prompt


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


def finalize_output(payload: Dict[str, Any], debug: bool) -> Dict[str, Any]:
    """
    Decide what to return to the caller.

    - debug=True: always return full payload
    - debug=False:
        - if task failed/blocked -> return full payload (keep errors visible)
        - if task succeeded -> return a stable summary
    """
    if debug:
        return payload

    results = payload.get("execution_results")
    if not isinstance(results, list) or not results:
        return payload

    # Find __meta__ row if present
    meta = None
    for r in results:
        if isinstance(r, dict) and r.get("step_id") == "__meta__":
            meta = r
            break

    task_status = None
    if isinstance(meta, dict):
        task_status = meta.get("task_status")

    # If task is not OK, return full payload for visibility
    if task_status in ("FAILED", "BLOCKED"):
        return payload

    # Otherwise: return a stable summary (still JSON-safe)
    # Prefer the last non-meta step as output source
    last_step = None
    for r in reversed(results):
        if isinstance(r, dict) and r.get("step_id") != "__meta__":
            last_step = r
            break

    summary: Dict[str, Any] = {
        "task_status": task_status or "OK",
    }

    if isinstance(meta, dict):
        stats = meta.get("stats")
        if isinstance(stats, dict):
            summary["stats"] = stats

    if isinstance(last_step, dict):
        summary["last_step_id"] = last_step.get("step_id")
        summary["tool"] = last_step.get("tool")
        if "output" in last_step:
            summary["output"] = last_step.get("output")

    return summary


def _build_pcl_schema_system_addendum() -> str:
    """
        Convert schema mode into a system message addendum.
        Best-effort: keep runner stable and auditable.
    """
    spec = SchemaSpec(
        name="plan_payload_v1",
        required_fields=["task_summary", "steps", "assumptions", "risks"],
    )
    base = (build_schema_prompt(spec) or "").strip()

    # 🔒 Strengthen the single most common failure mode:
    # step_id must start from step_1 and be continuous.
    step_index_contract = """
        Hard Rules (Step Index Contract):
        - steps MUST be ordered by step_id ascending.
        - step_id MUST start from "step_1".
        - step_id MUST be continuous with no gaps:
        "step_1", "step_2", ..., "step_N" (no skipping).
        - dependencies MUST only reference earlier declared step_ids.
    """.strip()
    string_escaping_contract = """
        Hard Rules (JSON String Escaping):
        - All string fields MUST be valid JSON strings.
        - Do NOT place unescaped double quotes (") inside any string field.
            Example (BAD):
            "acceptance": "output includes {"k":"v"}"
            Example (GOOD):
            "acceptance": "output includes {'k':'v'}"
            or
            "acceptance": "output includes a JSON object with keys k and v"
            or
            "acceptance": "output includes {\"k\":\"v\"}"
        - Prefer plain text in acceptance/deliverable; do not embed raw JSON snippets.
    """.strip()

    if base:
        return base + "\n\n" + step_index_contract + "\n\n" + string_escaping_contract
    return step_index_contract + "\n\n" + string_escaping_contract


def _save_debug_raw(filename: str, content: str) -> None:
    Path("docs-private/_debug").mkdir(parents=True, exist_ok=True)
    Path(f"docs-private/_debug/{filename}").write_text(content or "", encoding="utf-8")


def _call_model(
    messages: List[Dict[str, str]],
    *,
    temperature: float,
    max_tokens: int,
    service: Optional[ChatCompletionService] = None,
) -> str:
    svc = service or ChatCompletionService()
    raw = svc.create(
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return (raw or "").strip()


def _parse_json_best_effort(raw: str) -> Dict[str, Any]:
    """
    Best-effort parse:
    - tolerate fenced JSON (```json ... ```)
    - extract the outermost {...} region if extra text exists
    """
    text = (raw or "").strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # Try parse candidates by scanning '{' from right to left.
    # This is robust against outputs like: <explain>\n{...}\n\n{...}\n
    starts = [i for i, ch in enumerate(text) if ch == "{"]
    last_err: Optional[Exception] = None

    for i in reversed(starts):
        candidate = text[i:].strip()
        try:
            return json.loads(candidate)
        except Exception as e:
            last_err = e
            continue

    # Fallback: attempt the old outermost slice, then raise the last error
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
        return json.loads(candidate)

    if last_err is not None:
        raise last_err
    raise json.JSONDecodeError("No JSON object found in model output", text, 0)


def _enforce_expected_steps(payload: Dict[str, Any], expected_steps: Optional[int]) -> None:
    """
    Optional strictness hook (minimal B):
    - If expected_steps is set, require exactly N steps.
    - Require step_id set equals {"step_1", ..., "step_N"}.
    """
    if expected_steps is None:
        return

    steps = payload.get("steps")
    if not isinstance(steps, list):
        raise ValueError("expected_steps mismatch: steps must be an array")

    if len(steps) != expected_steps:
        raise ValueError(
            f"expected_steps mismatch: expected {expected_steps} steps, got {len(steps)}"
        )

    expected_ids = {f"step_{i}" for i in range(1, expected_steps + 1)}
    actual_ids = set()

    for s in steps:
        if isinstance(s, dict):
            sid = s.get("step_id")
            if isinstance(sid, str):
                actual_ids.add(sid)

    if actual_ids != expected_ids:
        raise ValueError(
            f"expected_steps mismatch: step_ids must be {sorted(expected_ids)}, got {sorted(actual_ids)}"
        )


def _needs_repair_due_to_validation(err: Exception) -> bool:
    """
    We repair on:
    - step_id sequencing (start from step_1 / contiguous)
    - expected_steps mismatch (optional strict mode)
    - JSON invalid (handled elsewhere)
    """
    msg = str(err)
    if "step_id sequence must start from step_1" in msg:
        return True
    if "step_id sequence must be contiguous" in msg:
        return True
    if "expected_steps mismatch" in msg:
        return True
    return False


def _build_repair_messages(
    *,
    base_system_prompt: str,
    schema_addendum: str,
    user_input: str,
    broken_text: str,
    expected_steps: Optional[int] = None,
) -> List[Dict[str, str]]:
    """
    Repair mode:
    - ALWAYS output a single valid JSON object (no markdown, no extra text)
    - Fix step_id numbering to start from step_1 and be continuous
    - Fix dependencies if renumbered
    - Also fix JSON escaping issues (e.g., quotes inside strings)
    - If expected_steps is provided, MUST output exactly N steps
    """
    expected_steps_rule = ""
    if expected_steps is not None:
        expected_steps_rule = f"""
    10) Expected step count (MUST):
    - You MUST output EXACTLY {expected_steps} steps.
    - step_ids MUST be step_1..step_{expected_steps}.
    - Do NOT drop steps. If the original has fewer steps, add minimal placeholder steps
      that preserve the user's intent and keep dependencies valid.
        """.strip()

    repair_system = f"""
    You are in REPAIR MODE.

    Goal:
    - Produce a SINGLE valid JSON object that matches the plan contract.

    Hard rules:
    1) Output MUST be a single valid JSON object. No extra text. No Markdown.
    2) Top-level fields MUST exist: task_summary (string), assumptions (string[]), risks (string[]), steps (array of objects).
    3) Each step MUST include: step_id, title, description, dependencies, deliverable, acceptance, tool.
    4) step_id MUST start from "step_1" and be continuous with no gaps: step_1..step_N.
    5) dependencies MUST only reference earlier step_ids. If you renumber step_ids, you MUST update dependencies accordingly.
    6) Ensure the JSON is valid: escape quotes inside strings properly.
    7) String safety (MUST):
    - Do NOT include raw double quotes (") inside any string field.
        If needed, escape as \"
    - Do NOT embed JSON objects/arrays inside strings (no '{{...}}' or '[...]' examples in acceptance/deliverable/title/description).
    - acceptance MUST be plain text (e.g., "output contains the word echo_tool"), never a JSON snippet.
    8) Renumbering (MUST):
    - If any step_id starts from step_2/step_3/... or step_1 is missing,
        you MUST renumber ALL steps to be sequential: step_1..step_N,
        preserving the original step order and updating dependencies accordingly.
    9) Curly-brace ban inside strings (MUST):
    - Do NOT include "{{" or "}}" or "[" or "]" in ANY string field
        (title/description/deliverable/acceptance/task_summary/assumptions/risks).
    - If you need to describe structure, use plain text (no braces).
    {expected_steps_rule}
    """.strip()

    user_repair = f"""
    User intent:
    {user_input.strip()}

    Broken model output (may be invalid JSON):
    {(broken_text or "").strip()}

    Task:
    Return a corrected JSON object only.
    """.strip()

    messages: List[Dict[str, str]] = [{"role": "system", "content": base_system_prompt}]
    if schema_addendum:
        messages.append({"role": "system", "content": schema_addendum})
    messages.append({"role": "system", "content": repair_system})
    messages.append({"role": "user", "content": user_repair})
    return messages


def run_agent_once_raw(
    user_input: str,
    *,
    prompt_path: str = "app/prompts/system/agent_system.md",
    temperature: float = 0.2,
    max_tokens: int = 512,
    schema_enabled: bool = True,
    service: Optional[ChatCompletionService] = None,
) -> str:
    """
    Run a single agent call and return raw text output.
    """
    system_prompt = load_text(prompt_path).strip()

    messages = [{"role": "system", "content": system_prompt}]

    # ✅ Optional schema control layer
    if schema_enabled:
        schema_addendum = _build_pcl_schema_system_addendum()
        if schema_addendum:
            messages.append({"role": "system", "content": schema_addendum})

    messages.append({"role": "user", "content": user_input.strip()})

    return _call_model(
        messages,
        temperature=temperature,
        max_tokens=max_tokens,
        service=service,
    )


def run_agent_once_json(
    user_input: str,
    *,
    prompt_path: str = "app/prompts/system/agent_system.md",
    temperature: float = 0.2,
    max_tokens: int = 512,
    debug: bool = False,
    schema_enabled: bool = True,
    expected_steps: Optional[int] = None,
    service: Optional[ChatCompletionService] = None,
) -> Dict[str, Any]:
    base_system_prompt = load_text(prompt_path).strip()

    schema_addendum = ""
    if schema_enabled:
        schema_addendum = _build_pcl_schema_system_addendum()

    # ---- Attempt #1 ----
    messages_1: List[Dict[str, str]] = [{"role": "system", "content": base_system_prompt}]
    if schema_addendum:
        messages_1.append({"role": "system", "content": schema_addendum})
    messages_1.append({"role": "user", "content": user_input.strip()})

    raw1 = _call_model(
        messages_1,
        temperature=temperature,
        max_tokens=max_tokens,
        service=service,
    )

    if not raw1 or not raw1.strip():
        raise ValueError("Model output is empty. Check API key/base_url/model, or prompt constraints.")

    # Parse attempt #1; if JSON invalid -> repair once
    try:
        payload1 = _parse_json_best_effort(raw1)
    except json.JSONDecodeError as e:
        _save_debug_raw("last_agent_raw_attempt1.txt", raw1)

        repair_messages = _build_repair_messages(
            base_system_prompt=base_system_prompt,
            schema_addendum=schema_addendum,
            user_input=user_input,
            broken_text=raw1,
            expected_steps=expected_steps,
        )
        raw2 = _call_model(
            repair_messages,
            temperature=0.0,
            max_tokens=max_tokens,
            service=service,
        )
        _save_debug_raw("last_agent_raw_attempt2.txt", raw2)

        try:
            payload2 = _parse_json_best_effort(raw2)
        except json.JSONDecodeError as e2:
            preview = (raw2 or "")[:200].replace("\n", "\\n")
            raise ValueError(
                f"Repair output is still not valid JSON: {e2}. Raw preview: {preview} "
                f"(saved to docs-private/_debug/last_agent_raw_attempt2.txt)"
            ) from e2

        # Validate repaired payload; fail-fast if still invalid (no loops)
        validate_payload(payload2)
        _enforce_expected_steps(payload2, expected_steps)

        payload2 = execute_plan(payload2)
        return finalize_output(payload2, debug)

    # Validate attempt #1; if step_id contract fails -> repair once
    try:
        validate_payload(payload1)
        _enforce_expected_steps(payload1, expected_steps)
    except ValueError as e:
        if _needs_repair_due_to_validation(e):
            _save_debug_raw("last_agent_raw_attempt1.txt", raw1)

            repair_messages = _build_repair_messages(
                base_system_prompt=base_system_prompt,
                schema_addendum=schema_addendum,
                user_input=user_input,
                broken_text=json.dumps(payload1, ensure_ascii=False, indent=2),
                expected_steps=expected_steps,
            )
            raw2 = _call_model(
                repair_messages,
                temperature=0.0,
                max_tokens=max_tokens,
                service=service,
            )
            _save_debug_raw("last_agent_raw_attempt2.txt", raw2)

            payload2 = _parse_json_best_effort(raw2)
            validate_payload(payload2)
            _enforce_expected_steps(payload2, expected_steps)

            payload2 = execute_plan(payload2)
            return finalize_output(payload2, debug)

        # Other validation errors: raise as-is
        raise

    # attempt #1 ok -> execute
    payload1 = execute_plan(payload1)
    return finalize_output(payload1, debug)
