import os

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen-plus")
LLM_API_BASE = os.getenv("LLM_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
LLM_API_KEY = os.getenv(
    "LLM_API_KEY",
    os.getenv("DASHSCOPE_API_KEY", os.getenv("OPENAI_API_KEY")),
)
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "300"))
