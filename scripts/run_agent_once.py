from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.agents.runner import load_text, run_agent_once_json


def save_text(path: str, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a single agent call with strict JSON output.")
    parser.add_argument("query", nargs="?", help="User query text")
    parser.add_argument("--input-file", help="Path to a text file containing the user query")
    parser.add_argument("--output-file", help="Save JSON output to a file (e.g., docs/samples/agent_output.json)")
    parser.add_argument("--debug", action="store_true", help="Print full payload including steps and execution_results")
    args = parser.parse_args()


    if args.input_file:
        user_input = load_text(args.input_file).strip()
    elif args.query:
        user_input = args.query.strip()
    else:
        print("Error: provide query text or --input-file", file=sys.stderr)
        raise SystemExit(2)

    payload = run_agent_once_json(
        user_input,
        prompt_path="app/prompts/system/agent_system.md",
        temperature=0.2,
        debug=args.debug,
    )

    pretty = json.dumps(payload, ensure_ascii=False, indent=2)

    if args.output_file:
        save_text(args.output_file, pretty + "\n")

    print(pretty)


if __name__ == "__main__":
    main()
