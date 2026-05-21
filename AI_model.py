import os
from typing import Any

import requests
from requests import HTTPError
from dotenv import load_dotenv

from config import (
    GITHUB_MODELS_API_VERSION,
    GITHUB_MODELS_BASE,
    LLM_API_BASE,
    LLM_API_KEY,
    LLM_MODEL,
    LLM_PROVIDER,
    LLM_TIMEOUT,
)


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
    "ollama/",
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

    @staticmethod
    def _strip_provider_prefix(model: str, provider: str) -> str:
        prefix = f"{provider}/"
        if model.lower().startswith(prefix):
            return model[len(prefix):]
        return model

    def complete(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        json_format: bool = False,
    ) -> str:
        if self.provider in ("ollama", "local"):
            return self._complete_ollama(
                system=system,
                user=user,
                temperature=temperature,
                max_tokens=max_tokens,
                json_format=json_format,
            )

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
        if self.provider in ("ollama", "local"):
            backend = "ollama"
            effective_model = self._strip_provider_prefix(self.model, "ollama")
        elif self.provider in ("github", "github_models", "global"):
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

    def _complete_ollama(
        self,
        *,
        system: str,
        user: str,
        temperature: float,
        max_tokens: int | None,
        json_format: bool,
    ) -> str:
        options = {"temperature": temperature}
        if max_tokens is not None:
            options["num_predict"] = max_tokens

        api_base = self.api_base or "http://127.0.0.1:11434"
        payload: dict[str, Any] = {
            "model": self._strip_provider_prefix(self.model, "ollama"),
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": options,
        }
        if json_format:
            payload["format"] = "json"

        resp = requests.post(
            f"{api_base.rstrip('/')}/api/chat",
            json=payload,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]

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
            raise
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


def get_client(model_mode: str | None = None) -> LLMClient:
    load_dotenv()
    mode = (model_mode or "open").strip().lower()

    if mode == "local":
        provider = os.getenv("LOCAL_LLM_PROVIDER", os.getenv("OLLAMA_PROVIDER", "ollama"))
        model = os.getenv("LOCAL_LLM_MODEL", os.getenv("OLLAMA_MODEL", "llama3"))
    else:
        provider = os.getenv("OPEN_LLM_PROVIDER", os.getenv("LLM_PROVIDER", os.getenv("OLLAMA_PROVIDER", LLM_PROVIDER)))
        model = os.getenv("OPEN_LLM_MODEL", os.getenv("LLM_MODEL", os.getenv("OLLAMA_MODEL", LLM_MODEL)))

    provider_key = provider.strip().lower()

    if provider_key in ("ollama", "local"):
        if mode == "local":
            api_base = os.getenv(
                "LOCAL_LLM_API_BASE",
                os.getenv("OLLAMA_HOST", os.getenv("LLM_API_BASE", LLM_API_BASE or "")),
            )
        else:
            api_base = os.getenv("OPEN_LLM_API_BASE", os.getenv("LLM_API_BASE", os.getenv("OLLAMA_HOST", LLM_API_BASE or "")))
    elif provider_key in ("github", "github_models", "global"):
        api_base = os.getenv("OPEN_LLM_API_BASE", os.getenv("LLM_API_BASE", GITHUB_MODELS_BASE))
    else:
        api_base = os.getenv("OPEN_LLM_API_BASE", os.getenv("LLM_API_BASE", LLM_API_BASE or ""))

    api_key = os.getenv("OPEN_LLM_API_KEY", os.getenv("LLM_API_KEY", os.getenv("GITHUB_TOKEN", LLM_API_KEY or "")))

    if not api_base and provider_key in ("ollama", "local"):
        api_base = "http://127.0.0.1:11434"
    if not api_base and provider_key in ("github", "github_models", "global"):
        api_base = GITHUB_MODELS_BASE

    return LLMClient(
        provider=provider,
        model=model,
        timeout=int(os.getenv("LLM_TIMEOUT", os.getenv("OLLAMA_TIMEOUT", str(LLM_TIMEOUT)))),
        api_base=api_base or None,
        api_key=api_key or None,
    )
