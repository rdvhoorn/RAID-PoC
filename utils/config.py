# config.py
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env into environment

config = {
    "INFERENCE_OUTPUT_DIR": os.getenv("INFERENCE_OUTPUT_DIR", "/tmp/raid_results"),
    "POLL_INTERVAL_SEC": int(os.getenv("POLL_INTERVAL_SEC", 1)),
    "MAX_POLL_ATTEMPTS": int(os.getenv("MAX_POLL_ATTEMPTS", 30)),
}