from agent_framework.openai import OpenAIChatClient

from config import (
    LMSTUDIO_API_KEY,
    LMSTUDIO_BASE_URL,
    LMSTUDIO_MODEL,
)


def create_client():
    return OpenAIChatClient(
        base_url=LMSTUDIO_BASE_URL,
        api_key=LMSTUDIO_API_KEY,
        model_id=LMSTUDIO_MODEL,
    )
