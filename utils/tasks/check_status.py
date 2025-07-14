import requests

API_URL = "http://localhost:8000/job_status"

def check_job_status(wsi_id: str):
    try:
        response = requests.get(f"{API_URL}/{wsi_id}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error checking job status: {e}")
        return None
