from __future__ import annotations

from app.core.prompts import load_prompt


def main() -> None:
    system_prompt = load_prompt("system_prompt")
    summary_prompt = load_prompt("summary_prompt")
    rag_prompt = load_prompt("rag_prompt")

    print("=== system_prompt ===")
    print(system_prompt)

    print("=== summary_prompt ===")
    print(summary_prompt)

    print("=== rag_prompt ===")
    print(rag_prompt)


if __name__ == "__main__":
    main()
