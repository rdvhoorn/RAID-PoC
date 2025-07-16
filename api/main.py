from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from api.schemas import RunJobRequest, JobStatusResponse
from api.middleware_logging import RequestIDMiddleware
from db.session import SessionLocal
from db.models import Job, JobStatusEnum
from tasks.slurm_tasks import run_slurm_inference
from utils.logging_config import get_and_configure_logger

_ = get_and_configure_logger("FastAPI")
app = FastAPI()
app.add_middleware(RequestIDMiddleware)

@app.post("/run_job")
def run_job(req: RunJobRequest, request: Request):
    log = request.state.logger
    log.info("job_submission_requested", wsi_id=req.wsi_id, tool_name=req.tool_name)
    
    session = SessionLocal()
    try:
        job = session.query(Job).filter_by(wsi_id=req.wsi_id, tool_name=req.tool_name).first()
        
        if not job:
            job = Job(wsi_id=req.wsi_id, tool_name=req.tool_name, status=JobStatusEnum.PENDING)
            session.add(job)
            session.commit()
            
            # Trigger SLURM task via Celery
            run_slurm_inference.delay(req.wsi_id, req.tool_name)
            
            log.info("job_created_and_submitted", job_id=job.job_id)
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"message": f"Created and submitted job with ID {job.job_id}."}
            )
        else:
            # Existing job found
            log.info("job_already_exists", job_id=job.job_id, status=job.status.value)
            return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={"message": f"Job previously {job.status.value.lower()} with job id {job.job_id}. Your request was not resubmitted."}
                )
    finally:
        session.close()

@app.get("/job_status/{wsi_id}_{tool_name}", response_model=JobStatusResponse)
def job_status(wsi_id: str, tool_name: str, request: Request):
    log = request.state.logger
    log.info("job_status_check_requested", wsi_id=wsi_id, tool_name=tool_name)
    
    session = SessionLocal()
    try:
        job = session.query(Job).filter_by(wsi_id=wsi_id, tool_name=tool_name).first()
        if not job:
            log.warning("job_status_not_found", wsi_id=wsi_id, tool_name=tool_name)
            raise HTTPException(status_code=404, detail="Job not found")
        
        log.info("job_status_returned", wsi_id=wsi_id, job_id=job.job_id, status=job.status.value)
        return JobStatusResponse(
            wsi_id=job.wsi_id,
            tool_name=job.tool_name,
            status=job.status.value,
        )
    finally:
        session.close()
