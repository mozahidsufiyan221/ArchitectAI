import os
import requests
from dotenv import load_dotenv

load_dotenv()

base = os.getenv(
    "LMSTUDIO_BASE_URL",
    "http://127.0.0.1:1234/v1",
).rstrip("/")

configured = os.getenv(
    "LMSTUDIO_MODEL",
    "qwen/qwen3.5-9b",
)

response = requests.get(
    f"{base}/models",
    timeout=10,
)

response.raise_for_status()

data = response.json()

print("LM Studio:", base)
print("Configured model:", configured)
print("\nModels returned by LM Studio:")

ids = []

for model in data.get("data", []):
    model_id = model.get("id")
    ids.append(model_id)
    print("  ", model_id)

if configured not in ids:
    print(
        "\nWARNING: configured model ID is not present in /v1/models.\n"
        "Set LMSTUDIO_MODEL in .env to the exact returned model ID."
    )
else:
    print("\nOK: configured model is available.")
