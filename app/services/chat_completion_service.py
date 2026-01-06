from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from openai import OpenAI


class ChatCompletionService:
    """
    Service layer for chat completions.

    - Owns OpenAI-compatible client creation and invocation.
    - Does NOT care about HTTP/FastAPI routing.
    - Returns plain text for now (minimal stable contract).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.model = model or os.getenv("OPENAI_MODEL")

        if not self.api_key:
            raise ValueError("Missing OPENAI_API_KEY")
        if not self.model:
            raise ValueError("Missing OPENAI_MODEL")

        # base_url can be None for real OpenAI; OK.
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def create(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> str:
        """
        Create a single-turn or multi-turn chat completion.

        The caller is responsible for providing messages.
        This service does not manage conversation state.
        """
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""
