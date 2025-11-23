from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, JSONBDict

class ProcessJob(Base):
    """
    Tracks the status of asynchronous background jobs.
    """
    __tablename__ = "process_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Celery Task ID
    task_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Job Type (e.g., "BATCH_PROCESS", "EXPORT")
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Status (QUEUED, PROCESSING, COMPLETED, FAILED)
    status: Mapped[str] = mapped_column(String(20), default="QUEUED")
    
    # Metadata / Input parameters
    params: Mapped[Optional[dict]] = mapped_column(JSONBDict, nullable=True)
    
    # Result / Error message
    result: Mapped[Optional[dict]] = mapped_column(JSONBDict, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
