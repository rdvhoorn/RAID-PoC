import sys
import requests
from utils.config import config

if __name__ == "__main__":
    job_id = sys.argv[1]
    try:
        resp = requests.post(
            f"{config["FASTAPI_HOST"]}:{config["FASTAPI_PORT"]}/finalize_job",
            json={"job_id": job_id}
        )
        resp.raise_for_status()
        print(f"Notification succeeded: {resp.status_code}")
    except Exception as e:
        print(f"Notification failed: {e}")
        sys.exit(1)
