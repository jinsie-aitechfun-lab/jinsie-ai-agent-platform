from __future__ import annotations

from pathlib import Path


_PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"


def load_prompt(name: str) -> str:
    """
    Load a prompt template from app/prompts/{name}.md.

    Example:
        load_prompt("system_prompt") -> content of app/prompts/system_prompt.md
    """
    path = _PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path}")
    return path.read_text(encoding="utf-8").strip() + "\n"
