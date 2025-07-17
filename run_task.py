# Client utility that uses the FastAPI endpoints instead of directly accessing the DB/Celery

import time
from utils.simulate_api_call.submit_job import submit_job
from utils.simulate_api_call.check_status import check_job_status
from utils.config import config
from pathlib import Path

wsi_id = "abc123"
tool_name = "cellvit"
output_dir = Path(config["INFERENCE_OUTPUT_DIR"])

# Step 1: Submit job via API
response = submit_job(wsi_id, tool_name)
if response:
    print("[1] Job submitted:", response)
else:
    exit(1)

# # Step 2: First status check (should still be running)
# time.sleep(2)
# status = check_job_status(wsi_id, tool_name)
# if status:
#     print("[2] First status check:", status)

# # Step 3: Poll for 2 minutes or until completed
# count = 0
# while status['status'] in ["PENDING", "RUNNING"] and count < 12:
#     time.sleep(10)
#     status = check_job_status(wsi_id, tool_name)
#     if status:
#         print(f"[{count}] Poll status check:", status)
        
#     count += 1

# # Step 4: Cleanup result and log files
# if status['status'] == "COMPLETED":
#     json_file = output_dir / f"{wsi_id}.json"
#     slurm_log = output_dir / f"slurm_{wsi_id}.out"

#     for file in [json_file, slurm_log]:
#         if file.exists():
#             file.unlink()
#             print(f"[4] Deleted file: {file}")
#         else:
#             print(f"[4] File not found for cleanup: {file}")
            
# else:
#     print("Because status 2 was not 'COMPLETED', output files were not deleted.")