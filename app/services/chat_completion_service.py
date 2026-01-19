from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, cast

import httpx
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
        *,
        timeout_seconds: Optional[float] = None,
        connect_timeout_seconds: Optional[float] = None,
        read_timeout_seconds: Optional[float] = None,
        max_retries: Optional[int] = None,
        trust_env: Optional[bool] = None,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.model = model or os.getenv("OPENAI_MODEL")

        if not self.api_key:
            raise ValueError("Missing OPENAI_API_KEY")
        if not self.model:
            raise ValueError("Missing OPENAI_MODEL")

        # ---- Timeouts (prevent "hang forever") ----
        # Prefer explicit args, then env, then defaults.
        # Note: httpx.Timeout supports granular settings; we keep it simple + safe.
        def _get_float_env(name: str) -> Optional[float]:
            v = os.getenv(name)
            if not v:
                return None
            try:
                return float(v)
            except ValueError:
                return None

        # Global fallback
        default_timeout = timeout_seconds
        if default_timeout is None:
            default_timeout = _get_float_env("OPENAI_TIMEOUT_SECONDS")
        if default_timeout is None:
            default_timeout = 30.0  # sane default

        # Granular overrides (optional)
        connect_t = connect_timeout_seconds
        if connect_t is None:
            connect_t = _get_float_env("OPENAI_CONNECT_TIMEOUT_SECONDS")
        if connect_t is None:
            connect_t = min(10.0, default_timeout)

        read_t = read_timeout_seconds
        if read_t is None:
            read_t = _get_float_env("OPENAI_READ_TIMEOUT_SECONDS")
        if read_t is None:
            read_t = default_timeout

        timeout = httpx.Timeout(
            timeout=default_timeout,
            connect=connect_t,
            read=read_t,
            write=default_timeout,
            pool=default_timeout,
        )

        # ---- trust_env (proxy) ----
        # Default: False to avoid accidental proxy/IDE env issues.
        # If you *need* env proxies, set OPENAI_TRUST_ENV=true
        def _get_bool_env(name: str) -> Optional[bool]:
            v = os.getenv(name)
            if v is None:
                return None
            v2 = v.strip().lower()
            if v2 in ("1", "true", "yes", "y", "on"):
                return True
            if v2 in ("0", "false", "no", "n", "off"):
                return False
            return None

        trust_env_final = trust_env
        if trust_env_final is None:
            trust_env_final = _get_bool_env("OPENAI_TRUST_ENV")
        if trust_env_final is None:
            trust_env_final = False

        http_client = httpx.Client(timeout=timeout, trust_env=trust_env_final)

        # ---- retries ----
        # Default: 0 (you already have repeat runner; retries can mask rate limits)
        retries = max_retries
        if retries is None:
            v = os.getenv("OPENAI_MAX_RETRIES")
            if v:
                try:
                    retries = int(v)
                except ValueError:
                    retries = None
        if retries is None:
            retries = 0

        # base_url can be None for real OpenAI; OK.
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            http_client=http_client,
            max_retries=retries,
        )

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
            model=cast(str, self.model),
            messages=cast(Any, messages),
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""
