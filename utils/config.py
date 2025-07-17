# config.py
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env into environment

config = {
    "INFERENCE_OUTPUT_DIR": os.getenv("INFERENCE_OUTPUT_DIR", "/tmp/raid_results"),
    "REDIS_LOCATION": os.getenv("REDIS_LOCATION", "redis://localhost:6379/0"),
    "POLL_INTERVAL_SEC": int(os.getenv("POLL_INTERVAL_SEC", 1)),
    "MAX_POLL_ATTEMPTS": int(os.getenv("MAX_POLL_ATTEMPTS", 30)),
    "DEVELOPER_MODE": os.getenv("DEVELOPER_MODE", "True"),
    "FASTAPI_HOST": os.getenv("FASTAPI_HOST", "http://localhost"),
    "FASTAPI_PORT": os.getenv("FASTAPI_PORT", 8000),
}