import os

from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

from config import ENDPOINT


def get_client() -> ChatCompletionsClient:
    load_dotenv()
    token = os.environ["GITHUB_TOKEN"]
    return ChatCompletionsClient(
        endpoint=ENDPOINT,
        credential=AzureKeyCredential(token),
    )
