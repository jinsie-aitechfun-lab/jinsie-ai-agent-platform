from pathlib import Path
import argparse
import json
import os
import sys

from openai import OpenAI


def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def save_text(path: str, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def validate_payload(payload: dict) -> None:
    required_top = {"task_summary", "steps", "assumptions", "risks"}
    missing = required_top - set(payload.keys())
    extra = set(payload.keys()) - required_top
    if missing:
        raise ValueError(f"Missing fields: {sorted(missing)}")
    if extra:
        raise ValueError(f"Unexpected fields: {sorted(extra)}")

    steps = payload["steps"]
    if not isinstance(steps, list) or len(steps) != 7:
        raise ValueError("steps must be a list of length 7")

    for i, s in enumerate(steps, start=1):
        if not isinstance(s, dict):
            raise ValueError(f"steps[{i}] must be an object")
        for k in ["day", "goal", "tasks", "deliverable"]:
            if k not in s:
                raise ValueError(f"steps[{i}] missing field: {k}")
        if s["day"] != i:
            raise ValueError(f"steps[{i}].day must be {i}")
        if not isinstance(s["tasks"], list) or len(s["tasks"]) < 3:
            raise ValueError(f"steps[{i}].tasks must be a list with >= 3 items")
        if not isinstance(s["deliverable"], str) or len(s["deliverable"].strip()) == 0:
            raise ValueError(f"steps[{i}].deliverable must be a non-empty string")


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

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
    )

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        temperature=0.2,
    )

    raw = response.choices[0].message.content
    payload = json.loads(raw)
    validate_payload(payload)

    pretty = json.dumps(payload, ensure_ascii=False, indent=2)

    if args.output_file:
        save_text(args.output_file, pretty + "\n")

    print(pretty)


if __name__ == "__main__":
    main()
