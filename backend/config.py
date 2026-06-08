import os

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "github")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
LLM_API_BASE = os.getenv("LLM_API_BASE")
LLM_API_KEY = os.getenv("LLM_API_KEY", os.getenv("GITHUB_TOKEN"))
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "300"))

GITHUB_MODELS_BASE = os.getenv("GITHUB_MODELS_BASE", "https://models.github.ai/inference")
GITHUB_MODELS_API_VERSION = os.getenv("GITHUB_MODELS_API_VERSION", "2026-03-10")
