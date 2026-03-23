import os

ENDPOINT = "https://models.github.ai/inference"

# Change model here -- any model available on GitHub Models works
# Examples: "microsoft/Phi-4", "openai/gpt-4.1", "meta/Llama-4-Scout-17B-16E-Instruct"
MODEL_NAME = os.getenv("MODEL_NAME", "microsoft/Phi-4")
