from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.process import Process
from app.models.process_data import ProcessData
from app.models.lot import Lot

class AsyncProcessService:
    """
    Service for handling process operations asynchronously.
    Designed for high-concurrency environments using SQLAlchemy AsyncSession.
    """
    
    async def start_process_async(
        self,
        db: AsyncSession,
        lot_id: int,
        process_id: int,
        operator_id: int
    ) -> ProcessData:
        """
        Start a process execution asynchronously.
        """
        # Fetch related data
        result = await db.execute(select(Process).where(Process.id == process_id))
        process = result.scalar_one_or_none()
        
        if not process:
            raise ValueError(f"Process {process_id} not found")

        # Create process data
        process_data = ProcessData(
            lot_id=lot_id,
            process_id=process_id,
            operator_id=operator_id,
            created_at=datetime.now(timezone.utc)
        )
        db.add(process_data)
        await db.commit()
        await db.refresh(process_data)
        
        return process_data

    async def complete_process_async(
        self,
        db: AsyncSession,
        process_data_id: int,
        result_status: str,
        measurements: Dict[str, Any]
    ) -> ProcessData:
        """
        Complete a process execution asynchronously.
        """
        result = await db.execute(select(ProcessData).where(ProcessData.id == process_data_id))
        process_data = result.scalar_one_or_none()
        
        if not process_data:
            raise ValueError(f"ProcessData {process_data_id} not found")
            
        process_data.result = result_status
        process_data.measurements = measurements
        process_data.completed_at = datetime.now(timezone.utc)
        
        # Calculate duration
        if process_data.created_at:
            duration = (process_data.completed_at - process_data.created_at).total_seconds()
            process_data.duration_seconds = duration
            
        await db.commit()
        await db.refresh(process_data)
        
        return process_data
