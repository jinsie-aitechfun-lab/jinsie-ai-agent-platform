from __future__ import annotations

import os
import sys

from openai import OpenAI

from app.core.prompts import load_prompt


def _required(name: str) -> str:
    v = os.getenv(name)
    if not v:
        print(f"[error] Missing env var: {name}", file=sys.stderr)
        sys.exit(2)
    return v


def main() -> None:
    # Keep code provider-agnostic: only read OpenAI-compatible env vars.
    api_key = _required("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")  # optional for real OpenAI
    model = os.getenv("OPENAI_MODEL", "qwen-plus")

    client = OpenAI(api_key=api_key, base_url=base_url)

    system_prompt = load_prompt("system_prompt")

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Hello! Briefly explain what an LLM is."},
        ],
        temperature=0.3,
    )

    print(resp.choices[0].message.content)


if __name__ == "__main__":
    main()
