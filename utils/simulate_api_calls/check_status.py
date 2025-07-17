import requests
from utils.config import config

API_URL = f"{config["FASTAPI_HOST"]}:{config["FASTAPI_PORT"]}/job_status"

def check_job_status(wsi_id: str, tool_name: str):
    try:
        response = requests.get(f"{API_URL}/{wsi_id}/{tool_name}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error checking job status: {e}")
        return None
