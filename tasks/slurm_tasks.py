# Defines a Celery task that submits a SLURM job and monitors it
# celery -A tasks.slurm_tasks worker --loglevel=info --concurrency=1 --pool=solo --logfile=celery.log

import subprocess
import time
from celery import Celery
from utils.config import config
from pathlib import Path

# Reuse your main Celery app definition
app = Celery('raid_tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@app.task
def run_slurm_inference(wsi_id: str):
    """Launch a SLURM job to simulate inference on a WSI."""
    print(f"Submitting SLURM job for WSI: {wsi_id}")

    # Submit SLURM job using sbatch
    result = subprocess.run(
        ["sbatch", "scripts/run_inference.sh", wsi_id, config["INFERENCE_OUTPUT_DIR"]],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        print(f"SLURM submission failed: {result.stderr}")
        return {"status": "ERROR", "error": result.stderr}

    # Extract SLURM job ID from output
    stdout = result.stdout.strip()
    print(f"SLURM submission output: {stdout}")
    job_id = stdout.split()[-1]

    # Optionally: poll for result file
    output_dir = Path(config["INFERENCE_OUTPUT_DIR"])  # from .env or config.py
    output_file = output_dir / f"{wsi_id}.json"  # matches script output
    for _ in range(config["MAX_POLL_ATTEMPTS"]):
        if subprocess.run(["test", "-f", output_file]).returncode == 0:
            print(f"Result file found: {output_file}")
            with open(output_file) as f:
                return f.read()
        time.sleep(config["POLL_INTERVAL_SEC"])

    return {"status": "TIMEOUT", "job_id": job_id}
