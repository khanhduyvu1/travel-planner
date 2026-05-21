import os

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", os.getenv("OLLAMA_MODEL", "llama3"))
LLM_API_BASE = os.getenv("LLM_API_BASE")
LLM_API_KEY = os.getenv("LLM_API_KEY", os.getenv("GITHUB_TOKEN"))
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", os.getenv("OLLAMA_TIMEOUT", "300")))

GITHUB_MODELS_BASE = os.getenv("GITHUB_MODELS_BASE", "https://models.github.ai/inference")
GITHUB_MODELS_API_VERSION = os.getenv("GITHUB_MODELS_API_VERSION", "2026-03-10")

# Backward-compatible names for older imports or existing local setup.
OLLAMA_HOST = os.getenv("OLLAMA_HOST", LLM_API_BASE or "http://127.0.0.1:11434")
OLLAMA_TIMEOUT = LLM_TIMEOUT
MODEL_NAME = LLM_MODEL
