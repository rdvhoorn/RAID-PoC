# Defines a Celery task that submits a SLURM job and monitors it
# celery -A tasks.slurm_tasks worker --loglevel=info --concurrency=1 --pool=solo --logfile=celery.log

import subprocess
from celery import Celery
from utils.config import config
from pathlib import Path

from db.session import SessionLocal
from db.models import Job, ResultFile, JobStatusEnum, FileStatusEnum
from utils.logging_config import get_and_configure_logger

# Reuse your main Celery app definition
app = Celery('raid_tasks', broker=config["REDIS_LOCATION"], backend=config["REDIS_LOCATION"])
app.conf.worker_hijack_root_logger = False 

# Get logger
log = get_and_configure_logger()

@app.task
def dispatch_fake_slurm_inference(wsi_id: str, tool_name: str):
    """Launch a SLURM job to simulate inference on a WSI."""    
    log.info("dispatch_inference_job_started", wsi_id=wsi_id, tool_name=tool_name)
    
    # Create DB session to interact with database
    session = SessionLocal()
    
    try:
        # Fetch corresponding job
        job = session.query(Job).filter_by(wsi_id=wsi_id, tool_name=tool_name).first()
        if not job:
            log.error("job_not_found", wsi_id=wsi_id, tool_name=tool_name)
            raise LookupError(f"No corresponding job found for WSI {wsi_id} and tool {tool_name}.")
        
        log.info("job_retrieved", job_id=job.job_id)

        # Submit SLURM job using sbatch
        result = subprocess.run(
            ["sbatch", "scripts/run_inference.sh", config["INFERENCE_OUTPUT_DIR"], str(job.job_id)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )

        # Handle faulting process
        if result.returncode != 0:
            log.error("slurm_submission_failed", job_id=job.job_id, stderr=result.stderr.strip())
            job.status = JobStatusEnum.FAILED
            session.commit()
            raise RuntimeError(f"SLURM submission failed for job_id={job.job_id}: {result.stderr.strip()}")
        
        # Update job status in database
        job.status = JobStatusEnum.RUNNING
        session.commit()
        log.info("slurm_job_running", job_id=job.job_id, status=job.status.value)

        # Define output paths for this inference job
        output_dir = Path(config["INFERENCE_OUTPUT_DIR"])
        json_path = output_dir / f"{job.job_id}.json"
        slurm_path = output_dir / f"slurm_{job.job_id}.out"
        
        # Add resultfiles to database
        for file_path, file_type in [(json_path, "json"), (slurm_path, "out")]:
            session.add(ResultFile(
                job_id=job.job_id,
                file_path=str(file_path),
                status=FileStatusEnum.RUNNING,
                file_type=file_type,
                description="inference_output"
            ))
        
        session.commit()
        log.info("job_dispatched_successfully", job_id=job.job_id)
    
    except (LookupError, RuntimeError):
        # Already logged above
        raise
    except Exception:
        # Unexpected crash
        log.exception("dispatch_fake_inference_crashed_unexpectedly", wsi_id=wsi_id, tool_name=tool_name)
        raise
    finally:
        session.close()
