import os
from dotenv import load_dotenv
from openai import OpenAI


def get_client() -> OpenAI:
    load_dotenv()

    token = os.environ["GITHUB_TOKEN"]
    endpoint = "https://models.github.ai/inference"

    return OpenAI(
        base_url=endpoint,
        api_key=token,
    )
