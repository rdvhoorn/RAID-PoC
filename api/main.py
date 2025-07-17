from fastapi import FastAPI, HTTPException, status, Request
from api.schemas import RunJobRequest, JobStatusResponse, FinalizeJobRequest
from api.middleware_logging import RequestIDMiddleware
from db.session import SessionLocal
from db.models import Job, JobStatusEnum, FileStatusEnum
from tasks.slurm_tasks import run_slurm_inference
from utils.logging_config import get_and_configure_logger
from pathlib import Path

_ = get_and_configure_logger()
app = FastAPI()
app.add_middleware(RequestIDMiddleware)

# TODO:
# Protect endpoints

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
            return {"message": f"Created and submitted job with ID {job.job_id}"}
        else:
            # Existing job found
            log.info("job_already_exists", job_id=job.job_id, status=job.status.value)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Job previously {job.status.value.lower()} with job id {job.job_id}. Your request was not resubmitted."
            )
    except HTTPException:
        raise
    except Exception as e:
        log.exception("job_submission_failed_unexpectedly", job_id=job.job_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="Job submission failed unexpectedly.")
    finally:
        session.close()

@app.get("/job_status/{wsi_id}/{tool_name}", response_model=JobStatusResponse)
def job_status(wsi_id: str, tool_name: str, request: Request):
    log = request.state.logger
    log.info("job_status_check_requested", wsi_id=wsi_id, tool_name=tool_name)
    
    session = SessionLocal()
    try:
        job = session.query(Job).filter_by(wsi_id=wsi_id, tool_name=tool_name).first()
        if not job:
            log.warning("job_status_not_found", wsi_id=wsi_id, tool_name=tool_name)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Job not found")
        
        log.info("job_status_returned", wsi_id=wsi_id, job_id=job.job_id, status=job.status.value)
        return JobStatusResponse(
            wsi_id=job.wsi_id,
            tool_name=job.tool_name,
            status=job.status.value,
        )
    except HTTPException:
        raise
    except Exception as e:
        log.exception("job_status_request_failed_unexpectedly", wsi_id=wsi_id, tool_name=tool_name)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Requesting job status failed unexpectedly")
    finally:
        session.close()

@app.post("/finalize_job")
def finalize_job(req: FinalizeJobRequest, request: Request):
    log = request.state.logger
    log.info("finalize_job_requested", job_id=req.job_id)

    session = SessionLocal()
    try:
        # Get job
        job = session.query(Job).filter_by(job_id=req.job_id).first()
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"Job with ID {req.job_id} not found.")

        log.info("job_to_finalize_found", job_id=job.job_id)
        job.status = JobStatusEnum.COMPLETED

        for file in job.result_files:
            if Path(file.file_path).exists():
                file.status = FileStatusEnum.COMPLETED
            else:
                job.status = JobStatusEnum.FAILED
                for f in job.result_files:
                    f.status = FileStatusEnum.FAILED
                session.commit()
                log.error("output_file_not_found", job_id=job.job_id, output_file_path=file.file_path)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                    detail=f"Missing output file: {file.file_path}")

        session.commit()
        log.info("job_finalization_completed", job_id=job.job_id)
        return {"status": "success", "job_id": job.job_id}
    except HTTPException:
        # Reraise above defined exceptions
        raise
    except Exception as e:
        log.exception("job_finalization_failed_unexpectedly", job_id=req.job_id, exception=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="Job finalization failed unexpectedly.")

    finally:
        session.close()
