from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api import deps
from app.models import User
from app.models.job import ProcessJob
from app.tasks.process_tasks import complete_process_batch, export_process_data
from app.core.celery_app import celery_app

router = APIRouter()

# --- Schemas ---
class BatchCompleteRequest(BaseModel):
    lot_id: int
    process_id: int
    batch_data: List[Dict[str, Any]]

class ExportRequest(BaseModel):
    start_date: str
    end_date: str
    format: str = "csv"

# --- Endpoints ---

@router.post("/process-data/batch-complete")
def batch_complete_process(
    request: BatchCompleteRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Submit batch process completion asynchronously.
    Returns a Job ID to track progress.
    """
    # 1. Trigger Celery Task
    task = complete_process_batch.delay(
        lot_id=request.lot_id,
        process_id=request.process_id,
        batch_data=request.batch_data
    )
    
    # 2. Create Job Record
    job = ProcessJob(
        task_id=task.id,
        job_type="BATCH_COMPLETE",
        status="QUEUED",
        params={
            "lot_id": request.lot_id, 
            "process_id": request.process_id,
            "count": len(request.batch_data)
        }
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "job_id": job.id,
        "task_id": task.id,
        "status": "QUEUED",
        "status_url": f"/api/v1/async/jobs/{job.id}"
    }

@router.post("/exports")
def export_data(
    request: ExportRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Trigger asynchronous data export.
    """
    task = export_process_data.delay(
        start_date=request.start_date,
        end_date=request.end_date,
        format=request.format
    )
    
    job = ProcessJob(
        task_id=task.id,
        job_type="DATA_EXPORT",
        status="QUEUED",
        params=request.dict()
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return {
        "job_id": job.id,
        "task_id": task.id,
        "status": "QUEUED",
        "status_url": f"/api/v1/async/jobs/{job.id}"
    }

@router.get("/jobs/{job_id}")
def get_job_status(
    job_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get current status of an async job.
    """
    job = db.query(ProcessJob).get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # Check Celery status
    task_result = celery_app.AsyncResult(job.task_id)
    
    # Update local DB status if changed
    if task_result.state != job.status:
        job.status = task_result.state
        if task_result.ready():
            if task_result.successful():
                job.result = task_result.result
            else:
                job.error_message = str(task_result.info)
        db.commit()
        
    return {
        "job_id": job.id,
        "task_id": job.task_id,
        "status": job.status,
        "progress": task_result.info if task_result.state == 'PROGRESS' else None,
        "result": job.result,
        "error": job.error_message
    }
