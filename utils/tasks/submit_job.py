import requests
from utils.config import config

API_URL = f"http://localhost:{config["FASTAPI_PORT"]}/run_job"

def submit_job(wsi_id: str, tool_name: str):
    payload = {"wsi_id": wsi_id, "tool_name": tool_name}
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        print(f"[HTTP ERROR] Status: {response.status_code}")
        print(f"[HTTP ERROR] Body: {response.text}")
    except requests.RequestException as e:
        print(f"[REQUEST ERROR] {e}")
