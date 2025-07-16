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
from utils.logging_config import get_and_configure_logger

# Reuse your main Celery app definition
app = Celery('raid_tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

# Get logger
log = get_and_configure_logger()

@app.task
def run_slurm_inference(wsi_id: str, tool_name: str):
    """Launch a SLURM job to simulate inference on a WSI."""    
    log.info("worker_started_run_slurm_inference", wsi_id=wsi_id, tool_name=tool_name)
    
    # Create DB session to interact with database
    session = SessionLocal()
    
    try:
        # Fetch corresponding job
        job = session.query(Job).filter_by(wsi_id=wsi_id, tool_name=tool_name).first()
        if not job:
            log.error("job_not_found", wsi_id=wsi_id, tool_name=tool_name)
            raise LookupError(f"No corresponding job found in DB for WSI {wsi_id} and tool {tool_name}.")
        
        log.info("job_retrieved", job_id=job.job_id)

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
        log.info("job_status_updated", job_id=job.job_id, status=job.status.value)

        # Handle faulting process
        if result.returncode != 0:
            log.error("slurm_submission_failed", job_id=job.job_id, stderr=result.stderr)
            job.status = JobStatusEnum.FAILED
            session.commit()
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
                            log.info("output_file_ready", path=str(output_file))
                            
                            job.status = JobStatusEnum.COMPLETED
                            session.add(ResultFile(
                                job_id=job.job_id,
                                file_path=str(output_file),
                                file_type="json",
                                description="SLURM job output"
                            ))
                            session.commit()
                            log.info("job_completed", job_id=job.job_id)
                            return {"status": "COMPLETED", "job_id": job.job_id}
                except json.JSONDecodeError:
                    # File may still be in the process of being written
                    pass

            time.sleep(config["POLL_INTERVAL_SEC"])

        # FAILED
        job.status = JobStatusEnum.FAILED
        session.commit()
        log.error("job_timeout", job_id=job.job_id)
        return {"status": "FAILED", "job_id": job.job_id}
    
    except Exception as e:
        log.exception("worker_run_slurm_inference_crashed", wsi_id=wsi_id, tool_name=tool_name)
        raise
    
    finally:
        session.close()
