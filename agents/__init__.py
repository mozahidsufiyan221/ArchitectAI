import os

from dotenv import load_dotenv
from agent_framework.openai import OpenAIChatClient

load_dotenv()


def create_client():
    return OpenAIChatClient(
        api_key="ollama",
        base_url=os.getenv(
            "OLLAMA_ENDPOINT",
            "http://localhost:11434/v1/"
        ),
        model=os.getenv(
            "OLLAMA_MODEL",
            "gemma4:e4b"
        ),
    )