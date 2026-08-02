import os
from typing import Any, Callable, cast

from dotenv import load_dotenv
from litellm import completion

from backend.config import (
    LLM_API_BASE,
    LLM_API_KEY,
    LLM_MODEL,
    LLM_PROVIDER,
    LLM_TIMEOUT,
)


class LLMRateLimitError(RuntimeError):
    pass


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

    def _is_gemini(self) -> bool:
        return self.provider in ("gemini", "google") or self.model.lower().startswith("gemini")

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
        return self._complete_litellm(
            system=system,
            user=user,
            temperature=temperature,
            max_tokens=max_tokens,
            json_format=json_format,
        )

    def info(self) -> dict[str, str | int | None]:
        return {
            "provider": self.provider,
            "backend": "litellm",
            "model": self._model_name(self.provider, self.model),
            "api_base": self.api_base,
            "timeout_seconds": self.timeout,
        }

    def _complete_litellm(
        self,
        *,
        system: str,
        user: str,
        temperature: float,
        max_tokens: int | None,
        json_format: bool,
    ) -> str:
        is_gemini = self._is_gemini()
        kwargs: dict[str, Any] = {
            "model": self._model_name(self.provider, self.model),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "timeout": self.timeout,
        }
        if not is_gemini:
            kwargs["temperature"] = temperature

        if max_tokens is not None:
            kwargs["max_tokens"] = max(max_tokens, int(os.getenv("LLM_MIN_OUTPUT_TOKENS", "64")))
            if is_gemini:
                kwargs["reasoning_effort"] = os.getenv("GEMINI_REASONING_EFFORT", "low")
        if json_format:
            kwargs["response_format"] = {"type": "json_object"}
        if self.api_base:
            kwargs["api_base"] = self.api_base
        if self.api_key:
            kwargs["api_key"] = self.api_key

        response = cast(Callable[..., Any], completion)(**kwargs)
        content = response.choices[0].message.content
        text = content if isinstance(content, str) else str(content or "")

        if not text.strip():
            retry_kwargs = dict(kwargs)
            retry_kwargs["max_tokens"] = max(
                int(retry_kwargs.get("max_tokens") or 0),
                int(os.getenv("LLM_RETRY_OUTPUT_TOKENS", "256")),
            )
            if is_gemini:
                retry_kwargs["reasoning_effort"] = os.getenv("GEMINI_REASONING_EFFORT", "low")
            response = cast(Callable[..., Any], completion)(**retry_kwargs)
            content = response.choices[0].message.content
            text = content if isinstance(content, str) else str(content or "")

        return text


def _api_key_for_provider(provider_key: str) -> str:
    generic_key = os.getenv("OPEN_LLM_API_KEY", os.getenv("LLM_API_KEY", ""))
    if generic_key:
        return generic_key

    provider_keys = {
        "gemini": ("GOOGLE_API_KEY", "GEMINI_API_KEY"),
        "google": ("GOOGLE_API_KEY", "GEMINI_API_KEY"),
        "openai": ("OPENAI_API_KEY",),
        "anthropic": ("ANTHROPIC_API_KEY",),
        "groq": ("GROQ_API_KEY",),
    }

    for env_name in provider_keys.get(provider_key, ()):
        api_key = os.getenv(env_name, "")
        if api_key:
            return api_key
    return LLM_API_KEY or ""


def get_client() -> LLMClient:
    load_dotenv(override=True)
    provider = os.getenv("OPEN_LLM_PROVIDER", os.getenv("LLM_PROVIDER", LLM_PROVIDER))
    model = os.getenv("OPEN_LLM_MODEL", os.getenv("LLM_MODEL", LLM_MODEL))

    provider_key = provider.strip().lower()
    api_base = os.getenv("OPEN_LLM_API_BASE", os.getenv("LLM_API_BASE", LLM_API_BASE or ""))

    api_key = _api_key_for_provider(provider_key)

    return LLMClient(
        provider=provider,
        model=model,
        timeout=int(os.getenv("LLM_TIMEOUT", str(LLM_TIMEOUT))),
        api_base=api_base or None,
        api_key=api_key or None,
    )
