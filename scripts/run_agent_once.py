from app.services.chat_completion_service import ChatCompletionService
from pathlib import Path
import argparse
import json
import os
import sys

from openai import OpenAI


def load_text(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {p.resolve()}")
    return Path(path).read_text(encoding="utf-8")


def save_text(path: str, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


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
        
        
def main():
    parser = argparse.ArgumentParser(description="Run a single agent call with strict JSON output.")
    parser.add_argument("query", nargs="?", help="User query text")
    parser.add_argument("--input-file", help="Path to a text file containing the user query")
    parser.add_argument("--output-file", help="Save JSON output to a file (e.g., docs/samples/agent_output.json)")
    args = parser.parse_args()

    if args.input_file:
        user_input = load_text(args.input_file).strip()
    elif args.query:
        user_input = args.query.strip()
    else:
        print("Error: provide query text or --input-file", file=sys.stderr)
        sys.exit(2)

    system_prompt = load_text("app/prompts/system//agent_system.md")

    service = ChatCompletionService()
    raw = service.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        temperature=0.2,
    )
    
    payload = json.loads(raw)
    validate_payload(payload)

    pretty = json.dumps(payload, ensure_ascii=False, indent=2)

    if args.output_file:
        save_text(args.output_file, pretty + "\n")

    print(pretty)


if __name__ == "__main__":
    main()
