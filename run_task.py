# run_task.py
# Manually registers a job in the DB and triggers the Celery SLURM task

from db.models import Job, JobStatusEnum
from db.session import SessionLocal
from tasks.slurm_tasks import run_slurm_inference

# Example values
wsi_id = "abc123"
tool_name = "cellvit"

# Step 1: Insert job into DB
session = SessionLocal()

# Check if job already exists
job = session.query(Job).filter_by(wsi_id=wsi_id, tool_name=tool_name).first()
if not job:
    job = Job(wsi_id=wsi_id, tool_name=tool_name, status=JobStatusEnum.PENDING)
    session.add(job)
    session.commit()
    print(f"Created new job with ID: {job.job_id}")
else:
    print(f"Job already exists with ID: {job.job_id}, status: {job.status}")

session.close()

# Step 2: Trigger Celery task
result = run_slurm_inference.delay(wsi_id, tool_name)
print("SLURM task submitted to Celery. Waiting for result...")

# Step 3: Wait for result (optional, only for dev/debug)
print(result.get(timeout=60))
