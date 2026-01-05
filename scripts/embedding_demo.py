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
    api_key = _required("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL")

    if not embedding_model:
        print("[error] Missing env var: OPENAI_EMBEDDING_MODEL", file=sys.stderr)
        print("Tip: set OPENAI_EMBEDDING_MODEL in your .envrc mapping for each provider.", file=sys.stderr)
        sys.exit(2)

    client = OpenAI(api_key=api_key, base_url=base_url)

    # Demo: prompts are reusable assets; we just reuse summary template as prefix.
    summary_prompt = load_prompt("summary_prompt")
    text = "AI developers build applications using large language models."
    input_text = f"{summary_prompt}\n\nCONTENT:\n{text}"

    resp = client.embeddings.create(
        model=embedding_model,
        input=input_text,
    )

    vec = resp.data[0].embedding
    print(f"Embedding dim: {len(vec)}")


if __name__ == "__main__":
    main()
