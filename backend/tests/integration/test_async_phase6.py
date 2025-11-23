import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.models.job import ProcessJob

client = TestClient(app)

@pytest.fixture
def mock_celery():
    with patch("app.api.v1.async_operations.complete_process_batch") as mock_batch, \
         patch("app.api.v1.async_operations.export_process_data") as mock_export:
        
        # Setup mock return values for .delay()
        mock_task = MagicMock()
        mock_task.id = "test-task-id-123"
        mock_batch.delay.return_value = mock_task
        mock_export.delay.return_value = mock_task
        
        yield mock_batch, mock_export

def test_batch_complete_endpoint(db, mock_celery, normal_user_token_headers):
    mock_batch, _ = mock_celery
    
    payload = {
        "lot_id": 1,
        "process_id": 1,
        "batch_data": [
            {"serial_number": "SN001", "result": "PASS"},
            {"serial_number": "SN002", "result": "FAIL"}
        ]
    }
    
    response = client.post(
        "/api/v1/async/process-data/batch-complete",
        json=payload,
        headers=normal_user_token_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "test-task-id-123"
    assert data["status"] == "QUEUED"
    
    # Verify DB record created
    job = db.query(ProcessJob).filter(ProcessJob.task_id == "test-task-id-123").first()
    assert job is not None
    assert job.job_type == "BATCH_COMPLETE"
    assert job.params["count"] == 2

def test_export_endpoint(db, mock_celery, normal_user_token_headers):
    _, mock_export = mock_celery
    
    payload = {
        "start_date": "2023-01-01",
        "end_date": "2023-01-31",
        "format": "csv"
    }
    
    response = client.post(
        "/api/v1/async/exports",
        json=payload,
        headers=normal_user_token_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "test-task-id-123"
    
    # Verify DB record
    job = db.query(ProcessJob).filter(ProcessJob.task_id == "test-task-id-123").first()
    assert job is not None
    assert job.job_type == "DATA_EXPORT"
