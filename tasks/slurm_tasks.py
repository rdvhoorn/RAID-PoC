# Defines a Celery task that submits a SLURM job and monitors it
# celery -A tasks.slurm_tasks worker --loglevel=info --concurrency=1 --pool=solo --logfile=celery.log

import subprocess
import time
import os
from celery import Celery
from utils.config import config
from pathlib import Path
import json

from db.session import SessionLocal
from db.models import Job, ResultFile, JobStatusEnum

# Reuse your main Celery app definition
app = Celery('raid_tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@app.task
def run_slurm_inference(wsi_id: str, tool_name: str):
    """Launch a SLURM job to simulate inference on a WSI."""    
    # Create DB session to interact with database
    session = SessionLocal()
    
    # Fetch corresponding job
    job = session.query(Job).filter_by(wsi_id=wsi_id, tool_name=tool_name).first()
    job_id = job.job_id
    if not job:
        session.close()
        raise ValueError(f"No corresponding job found in DB for WSI {wsi_id} and tool {tool_name}.")
    
    print(f"Running SLURM job for existing job ID: {job_id}")

    # Submit SLURM job using sbatch
    result = subprocess.run(
        ["sbatch", "scripts/run_inference.sh", wsi_id, config["INFERENCE_OUTPUT_DIR"]],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Update job status in database
    job.status = JobStatusEnum.RUNNING
    session.commit()

    # Handle faulting process
    if result.returncode != 0:
        print(f"SLURM submission failed: {result.stderr}")
        job.status = JobStatusEnum.FAILED
        session.commit()
        session.close()
        return {"status": "FAILED", "error": result.stderr}

    # Format output path
    output_dir = Path(config["INFERENCE_OUTPUT_DIR"])  # from .env or config.py
    output_file = output_dir / f"{wsi_id}.json"  # matches script output
    
    # Poll for output file
    for _ in range(config["MAX_POLL_ATTEMPTS"]):
        if os.path.isfile(output_file):
            try:
                with open(output_file, "r") as f:
                    data = json.load(f)
                    if data.get("status") == "COMPLETED":
                        print(f"Result file complete: {output_file}")
                        
                        job.status = JobStatusEnum.COMPLETED
                        session.add(ResultFile(
                            job_id=job_id,
                            file_path=str(output_file),
                            file_type="json",
                            description="SLURM job output"
                        ))
                        session.commit()
                        session.close()
                        return {"status": "COMPLETED", "job_id": job_id}
            except json.JSONDecodeError:
                # File may still be in the process of being written
                pass

        time.sleep(config["POLL_INTERVAL_SEC"])

    # Timeout
    job.status = JobStatusEnum.TIMEOUT
    session.commit()
    session.close()
    return {"status": "TIMEOUT", "job_id": job_id}
