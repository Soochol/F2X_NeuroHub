import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.analytics.metrics_aggregator import MetricsAggregator
from app.analytics.alert_manager import AlertManager
from app.models.process_data import ProcessData, ProcessResult
from app.models.process import Process
from app.models.equipment import Equipment
from app.models.user import User

def test_metrics_aggregator_success_rate(db: Session):
    # Setup data
    process = Process(process_code="TEST_PROC", process_name_ko="Test", process_name_en="Test")
    db.add(process)
    db.commit()
    
    # Add 4 passes, 1 fail
    for i in range(5):
        pd = ProcessData(
            process_id=process.id,
            result=ProcessResult.PASS if i < 4 else ProcessResult.FAIL,
            created_at=datetime.now(timezone.utc)
        )
        db.add(pd)
    db.commit()
    
    # Test
    metrics = MetricsAggregator.aggregate_process_success_rate(db, process.id)
    assert metrics["total_runs"] == 5
    assert metrics["failures"] == 1
    assert metrics["success_rate"] == 0.8

def test_alert_manager_failure_rate(db: Session):
    # Setup data
    process = Process(process_code="TEST_ALERT", process_name_ko="Alert", process_name_en="Alert")
    db.add(process)
    db.commit()
    
    # Add 6 failures (100% fail rate)
    for i in range(6):
        pd = ProcessData(
            process_id=process.id,
            result=ProcessResult.FAIL,
            created_at=datetime.now(timezone.utc)
        )
        db.add(pd)
    db.commit()
    
    manager = AlertManager(db)
    alert = manager.check_process_failure_rate(process.id, threshold=0.1)
    
    assert alert is not None
    assert alert["type"] == "PROCESS_FAILURE_RATE_HIGH"
    assert "100.0%" in alert["message"]

def test_equipment_utilization(db: Session):
    equipment = Equipment(
        equipment_code="TEST_EQ", 
        equipment_name="Test Eq", 
        equipment_type="TEST",
        status="AVAILABLE"
    )
    db.add(equipment)
    db.commit()
    
    # Add 1 hour of runtime
    pd = ProcessData(
        equipment_id=equipment.id,
        duration_seconds=3600,
        created_at=datetime.now(timezone.utc)
    )
    db.add(pd)
    db.commit()
    
    # Window 1 hour -> 100% utilization
    metrics = MetricsAggregator.aggregate_equipment_utilization(db, equipment.id, time_window_hours=1)
    assert metrics["utilization_percent"] == 1.0
    assert metrics["uptime_hours"] == 1.0
