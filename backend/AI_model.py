import os
import time
from typing import Any

import requests
from requests import HTTPError
from dotenv import load_dotenv

from backend.config import (
    GITHUB_MODELS_API_VERSION,
    GITHUB_MODELS_BASE,
    LLM_API_BASE,
    LLM_API_KEY,
    LLM_MODEL,
    LLM_PROVIDER,
    LLM_TIMEOUT,
)


class LLMRateLimitError(RuntimeError):
    pass


def _retry_delay(retry_after: str, attempt: int) -> float:
    try:
        return min(float(retry_after), 8.0)
    except (TypeError, ValueError):
        return min(2.0 ** attempt, 8.0)


KNOWN_PROVIDER_PREFIXES = (
    "anthropic/",
    "azure/",
    "bedrock/",
    "cohere/",
    "deepseek/",
    "gemini/",
    "groq/",
    "huggingface/",
    "mistral/",
    "openai/",
    "openrouter/",
    "perplexity/",
    "together_ai/",
    "vertex_ai/",
)


class LLMClient:
    def __init__(
        self,
        model: str = LLM_MODEL,
        provider: str = LLM_PROVIDER,
        timeout: int = LLM_TIMEOUT,
        api_base: str | None = LLM_API_BASE,
        api_key: str | None = LLM_API_KEY,
    ) -> None:
        self.provider = provider.strip().lower()
        self.model = model.strip()
        self.timeout = timeout
        self.api_base = api_base
        self.api_key = api_key

    @staticmethod
    def _model_name(provider: str, model: str) -> str:
        model = model.strip()
        provider = provider.strip().lower()
        model_lower = model.lower()

        if not provider or model_lower.startswith(KNOWN_PROVIDER_PREFIXES):
            return model
        return f"{provider}/{model}"

    def complete(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        json_format: bool = False,
    ) -> str:
        if self.provider in ("github", "github_models", "global"):
            return self._complete_github(
                system=system,
                user=user,
                temperature=temperature,
                max_tokens=max_tokens,
                json_format=json_format,
            )

        return self._complete_litellm(
            system=system,
            user=user,
            temperature=temperature,
            max_tokens=max_tokens,
            json_format=json_format,
        )

    def info(self) -> dict[str, str | int | None]:
        if self.provider in ("github", "github_models", "global"):
            backend = "github_models"
            effective_model = self.model
        else:
            backend = "litellm"
            effective_model = self._model_name(self.provider, self.model)

        return {
            "provider": self.provider,
            "backend": backend,
            "model": effective_model,
            "api_base": self.api_base,
            "timeout_seconds": self.timeout,
        }

    def _complete_github(
        self,
        *,
        system: str,
        user: str,
        temperature: float,
        max_tokens: int | None,
        json_format: bool,
    ) -> str:
        if not self.api_key:
            raise RuntimeError("GitHub Models requires GITHUB_TOKEN or LLM_API_KEY.")

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if json_format:
            payload["response_format"] = {"type": "json_object"}

        api_base = self.api_base or GITHUB_MODELS_BASE
        max_retries = int(os.getenv("LLM_MAX_RETRIES", "2"))
        retry_after = ""

        for attempt in range(max_retries + 1):
            resp = requests.post(
                f"{api_base.rstrip('/')}/chat/completions",
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "X-GitHub-Api-Version": GITHUB_MODELS_API_VERSION,
                },
                json=payload,
                timeout=self.timeout,
            )
            retry_after = resp.headers.get("Retry-After", "")

            if resp.status_code == 429 and attempt < max_retries:
                time.sleep(_retry_delay(retry_after, attempt))
                continue

            try:
                resp.raise_for_status()
            except HTTPError as exc:
                if resp.status_code == 401:
                    raise RuntimeError(
                        "GitHub Models returned 401 Unauthorized. Check that GITHUB_TOKEN "
                        "or LLM_API_KEY is valid, not expired, and has access to GitHub Models."
                    ) from exc
                if resp.status_code == 403:
                    raise RuntimeError(
                        "GitHub Models returned 403 Forbidden. Your token is valid, but it "
                        "does not appear to have permission to use GitHub Models."
                    ) from exc
                if resp.status_code == 429:
                    suffix = f" Retry after {retry_after} seconds." if retry_after else ""
                    raise LLMRateLimitError(
                        "GitHub Models rate limit reached. Wait a bit and try again, "
                        "or switch to another LLM provider in .env." + suffix
                    ) from exc
                raise
            break

        return resp.json()["choices"][0]["message"]["content"]

    def _complete_litellm(
        self,
        *,
        system: str,
        user: str,
        temperature: float,
        max_tokens: int | None,
        json_format: bool,
    ) -> str:
        kwargs: dict[str, Any] = {
            "model": self._model_name(self.provider, self.model),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "timeout": self.timeout,
        }

        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        if json_format:
            kwargs["response_format"] = {"type": "json_object"}
        if self.api_base:
            kwargs["api_base"] = self.api_base
        if self.api_key:
            kwargs["api_key"] = self.api_key

        from litellm import completion

        response = completion(**kwargs)
        content = response.choices[0].message.content
        if isinstance(content, str):
            return content
        return str(content or "")


def get_client() -> LLMClient:
    load_dotenv()
    provider = os.getenv("OPEN_LLM_PROVIDER", os.getenv("LLM_PROVIDER", LLM_PROVIDER))
    model = os.getenv("OPEN_LLM_MODEL", os.getenv("LLM_MODEL", LLM_MODEL))

    provider_key = provider.strip().lower()

    if provider_key in ("github", "github_models", "global"):
        api_base = os.getenv("OPEN_LLM_API_BASE", os.getenv("LLM_API_BASE", GITHUB_MODELS_BASE))
    else:
        api_base = os.getenv("OPEN_LLM_API_BASE", os.getenv("LLM_API_BASE", LLM_API_BASE or ""))

    api_key = os.getenv("OPEN_LLM_API_KEY", os.getenv("LLM_API_KEY", os.getenv("GITHUB_TOKEN", LLM_API_KEY or "")))

    if not api_base and provider_key in ("github", "github_models", "global"):
        api_base = GITHUB_MODELS_BASE

    return LLMClient(
        provider=provider,
        model=model,
        timeout=int(os.getenv("LLM_TIMEOUT", str(LLM_TIMEOUT))),
        api_base=api_base or None,
        api_key=api_key or None,
    )
