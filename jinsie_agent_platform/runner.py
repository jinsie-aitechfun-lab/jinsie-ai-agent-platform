"""
Thin wrapper to expose stable imports for system repos.

DO NOT implement business logic here.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

# Map to the real runner entry in your platform.
from app.agents.runner import run_agent_once_json


def workflow_runner(
    user_input: str,
    *,
    debug: bool = False,
    expected_steps: Optional[int] = None,
    strict_degraded: bool = False,
    prompt_path: str = "app/prompts/system/agent_system.md",
    temperature: float = 0.2,
    max_tokens: int = 512,
) -> Dict[str, Any]:
    """
    Stable entry for system repos.

    This is a thin wrapper that forwards to the platform runner.
    """
    return run_agent_once_json(
        user_input,
        prompt_path=prompt_path,
        temperature=temperature,
        max_tokens=max_tokens,
        debug=debug,
        expected_steps=expected_steps,
        strict_degraded=strict_degraded,
    )
