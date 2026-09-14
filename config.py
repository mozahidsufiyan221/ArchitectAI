import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

LMSTUDIO_BASE_URL = os.getenv(
    "LMSTUDIO_BASE_URL",
    "http://127.0.0.1:1234/v1",
).rstrip("/")

LMSTUDIO_MODEL = os.getenv(
    "LMSTUDIO_MODEL",
    "qwen/qwen3.5-9b",
)

LMSTUDIO_API_KEY = os.getenv(
    "LMSTUDIO_API_KEY",
    "lm-studio",
)

REVIT_MCP_URL = os.getenv(
    "REVIT_MCP_URL",
    "http://127.0.0.1:8765/mcp",
)

SBC_INDEX_DIR = ROOT / os.getenv(
    "SBC_INDEX_DIR",
    "data/sbc_index",
)

PROJECTS_DIR = ROOT / os.getenv(
    "PROJECTS_DIR",
    "data/projects",
)

SBC_SOURCE_DIR = ROOT / os.getenv(
    "SBC_SOURCE_DIR",
    "data/sbc",
)

SBC_TOP_K = int(os.getenv("SBC_TOP_K", "6"))

for directory in (SBC_INDEX_DIR, PROJECTS_DIR, SBC_SOURCE_DIR):
    directory.mkdir(parents=True, exist_ok=True)
