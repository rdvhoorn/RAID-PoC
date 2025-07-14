from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from api.schemas import RunJobRequest, JobStatusResponse
from db.session import SessionLocal
from db.models import Job, JobStatusEnum
from tasks.slurm_tasks import run_slurm_inference

app = FastAPI()

@app.post("/run_job")
def run_job(req: RunJobRequest):
    session = SessionLocal()
    try:
        job = session.query(Job).filter_by(wsi_id=req.wsi_id, tool_name=req.tool_name).first()
        if not job:
            job = Job(wsi_id=req.wsi_id, tool_name=req.tool_name, status=JobStatusEnum.PENDING)
            session.add(job)
            session.commit()
            # Trigger SLURM task via Celery
            run_slurm_inference.delay(req.wsi_id, req.tool_name)
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"message": f"Created and submitted job with ID {job.job_id}."}
            )
        else:
            # Existing job found
            return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={"message": f"Job previously {job.status.value.lower()} with job id {job.job_id}. Your request was not resubmitted."}
                )
    finally:
        session.close()

@app.get("/job_status/{wsi_id}", response_model=JobStatusResponse)
def job_status(wsi_id: str):
    session = SessionLocal()
    try:
        job = session.query(Job).filter_by(wsi_id=wsi_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return JobStatusResponse(
            wsi_id=job.wsi_id,
            tool_name=job.tool_name,
            status=job.status.value,
        )
    finally:
        session.close()
