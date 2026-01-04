"""
Integration tests for Reports API endpoints.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from station_service.api import create_app
from station_service.storage.database import Database


# ============================================================================
# Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def test_database(temp_db_path):
    """Create and initialize a test database with sample data."""
    db = await Database.create(temp_db_path)
    await db.init_db()

    # Insert sample execution data
    await _insert_sample_executions(db)

    yield db
    await db.close()


async def _insert_sample_executions(db: Database):
    """Insert sample execution results for testing."""
    batch_id = "test-batch-001"
    now = datetime.now()

    # Insert 10 executions (7 pass, 3 fail)
    for i in range(10):
        execution_id = f"exec-{i:03d}"
        status = "PASS" if i < 7 else "FAIL"
        started_at = now - timedelta(hours=10 - i)
        completed_at = started_at + timedelta(seconds=5 + i)
        duration = (completed_at - started_at).total_seconds() * 1000

        await db.execution_repository.save_execution({
            "id": execution_id,
            "batch_id": batch_id,
            "sequence_name": "test_sequence",
            "sequence_version": "1.0.0",
            "status": status,
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "duration": duration,
            "parameters": {},
        })

        # Insert step results
        await db.execution_repository.save_step_result({
            "id": f"{execution_id}-step-1",
            "execution_id": execution_id,
            "step_name": "Initialize",
            "order": 1,
            "status": "PASS",
            "started_at": started_at.isoformat(),
            "completed_at": (started_at + timedelta(seconds=1)).isoformat(),
            "duration": 1000,
            "result": {},
        })

        await db.execution_repository.save_step_result({
            "id": f"{execution_id}-step-2",
            "execution_id": execution_id,
            "step_name": "Execute",
            "order": 2,
            "status": status,
            "started_at": (started_at + timedelta(seconds=1)).isoformat(),
            "completed_at": completed_at.isoformat(),
            "duration": duration - 1000,
            "result": {},
            "error_message": "Test failed" if status == "FAIL" else None,
        })


@pytest_asyncio.fixture
async def app_with_db(test_database, station_config, event_emitter, mock_ipc_server):
    """Create a test app with database."""
    from station_service.batch.manager import BatchManager

    app = create_app()

    batch_manager = BatchManager(
        config=station_config,
        ipc_server=mock_ipc_server,
        event_emitter=event_emitter,
    )

    app.state.config = station_config
    app.state.database = test_database
    app.state.batch_manager = batch_manager
    app.state.event_emitter = event_emitter
    app.state.sync_engine = None

    yield app

    if batch_manager.is_running:
        await batch_manager.stop()


@pytest_asyncio.fixture
async def client(app_with_db):
    """Create an async test client."""
    transport = ASGITransport(app=app_with_db)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ============================================================================
# Batch Summary Report Tests
# ============================================================================


class TestBatchSummaryReportAPI:
    """Tests for /api/reports/batch/{batch_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_batch_summary_json(self, client):
        """Test getting batch summary report in JSON format."""
        response = await client.get(
            "/api/reports/batch/test-batch-001",
            params={"format": "json"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["batch_id"] == "test-batch-001"
        assert data["data"]["total_executions"] == 10
        assert data["data"]["pass_count"] == 7
        assert data["data"]["fail_count"] == 3

    @pytest.mark.asyncio
    async def test_get_batch_summary_with_batch_name(self, client):
        """Test getting batch summary with batch name parameter."""
        response = await client.get(
            "/api/reports/batch/test-batch-001",
            params={"format": "json", "batch_name": "My Test Batch"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["batch_name"] == "My Test Batch"

    @pytest.mark.asyncio
    async def test_get_batch_summary_xlsx(self, client):
        """Test getting batch summary report in Excel format."""
        response = await client.get(
            "/api/reports/batch/test-batch-001",
            params={"format": "xlsx"},
        )

        assert response.status_code == 200
        assert "spreadsheetml" in response.headers["content-type"]
        assert response.content[:4] == b"PK\x03\x04"  # ZIP magic bytes

    @pytest.mark.asyncio
    async def test_get_batch_summary_pdf(self, client):
        """Test getting batch summary report in PDF format."""
        response = await client.get(
            "/api/reports/batch/test-batch-001",
            params={"format": "pdf"},
        )

        assert response.status_code == 200
        assert "pdf" in response.headers["content-type"]
        assert response.content[:4] == b"%PDF"

    @pytest.mark.asyncio
    async def test_get_batch_summary_csv(self, client):
        """Test getting batch summary report in CSV format."""
        response = await client.get(
            "/api/reports/batch/test-batch-001",
            params={"format": "csv"},
        )

        assert response.status_code == 200
        assert "csv" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_get_batch_summary_not_found(self, client):
        """Test getting batch summary for non-existent batch."""
        response = await client.get(
            "/api/reports/batch/non-existent-batch",
            params={"format": "json"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_batch_summary_includes_steps(self, client):
        """Test that batch summary includes step statistics."""
        response = await client.get(
            "/api/reports/batch/test-batch-001",
            params={"format": "json"},
        )

        assert response.status_code == 200
        data = response.json()
        steps = data["data"]["steps"]
        assert len(steps) == 2
        assert any(s["step_name"] == "Initialize" for s in steps)
        assert any(s["step_name"] == "Execute" for s in steps)


# ============================================================================
# Period Statistics Report Tests
# ============================================================================


class TestPeriodStatisticsReportAPI:
    """Tests for /api/reports/period endpoint."""

    @pytest.mark.asyncio
    async def test_get_period_stats_daily(self, client):
        """Test getting daily period statistics."""
        from_date = (datetime.now() - timedelta(days=7)).isoformat()
        to_date = datetime.now().isoformat()

        response = await client.get(
            "/api/reports/period",
            params={
                "period": "daily",
                "from": from_date,
                "to": to_date,
                "format": "json",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["period_type"] == "daily"

    @pytest.mark.asyncio
    async def test_get_period_stats_weekly(self, client):
        """Test getting weekly period statistics."""
        from_date = (datetime.now() - timedelta(days=30)).isoformat()
        to_date = datetime.now().isoformat()

        response = await client.get(
            "/api/reports/period",
            params={
                "period": "weekly",
                "from": from_date,
                "to": to_date,
                "format": "json",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["period_type"] == "weekly"

    @pytest.mark.asyncio
    async def test_get_period_stats_monthly(self, client):
        """Test getting monthly period statistics."""
        from_date = (datetime.now() - timedelta(days=90)).isoformat()
        to_date = datetime.now().isoformat()

        response = await client.get(
            "/api/reports/period",
            params={
                "period": "monthly",
                "from": from_date,
                "to": to_date,
                "format": "json",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["period_type"] == "monthly"

    @pytest.mark.asyncio
    async def test_get_period_stats_invalid_date_range(self, client):
        """Test getting period stats with invalid date range."""
        response = await client.get(
            "/api/reports/period",
            params={
                "period": "daily",
                "from": datetime.now().isoformat(),
                "to": (datetime.now() - timedelta(days=7)).isoformat(),  # to < from
                "format": "json",
            },
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_period_stats_with_batch_filter(self, client):
        """Test getting period stats filtered by batch."""
        from_date = (datetime.now() - timedelta(days=7)).isoformat()
        to_date = datetime.now().isoformat()

        response = await client.get(
            "/api/reports/period",
            params={
                "period": "daily",
                "from": from_date,
                "to": to_date,
                "batch_id": "test-batch-001",
                "format": "json",
            },
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_period_stats_xlsx(self, client):
        """Test getting period stats in Excel format."""
        from_date = (datetime.now() - timedelta(days=7)).isoformat()
        to_date = datetime.now().isoformat()

        response = await client.get(
            "/api/reports/period",
            params={
                "period": "daily",
                "from": from_date,
                "to": to_date,
                "format": "xlsx",
            },
        )

        assert response.status_code == 200
        assert "spreadsheetml" in response.headers["content-type"]


# ============================================================================
# Step Analysis Report Tests
# ============================================================================


class TestStepAnalysisReportAPI:
    """Tests for /api/reports/step-analysis endpoint."""

    @pytest.mark.asyncio
    async def test_get_step_analysis(self, client):
        """Test getting step analysis report."""
        response = await client.get(
            "/api/reports/step-analysis",
            params={"format": "json"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "steps" in data["data"]
        assert data["data"]["total_steps"] >= 0

    @pytest.mark.asyncio
    async def test_get_step_analysis_with_filters(self, client):
        """Test getting step analysis with date filters."""
        from_date = (datetime.now() - timedelta(days=7)).isoformat()
        to_date = datetime.now().isoformat()

        response = await client.get(
            "/api/reports/step-analysis",
            params={
                "from": from_date,
                "to": to_date,
                "format": "json",
            },
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_step_analysis_with_batch_filter(self, client):
        """Test getting step analysis filtered by batch."""
        response = await client.get(
            "/api/reports/step-analysis",
            params={
                "batch_id": "test-batch-001",
                "format": "json",
            },
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_step_analysis_xlsx(self, client):
        """Test getting step analysis in Excel format."""
        response = await client.get(
            "/api/reports/step-analysis",
            params={"format": "xlsx"},
        )

        assert response.status_code == 200
        assert "spreadsheetml" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_get_step_analysis_pdf(self, client):
        """Test getting step analysis in PDF format."""
        response = await client.get(
            "/api/reports/step-analysis",
            params={"format": "pdf"},
        )

        assert response.status_code == 200
        assert "pdf" in response.headers["content-type"]


# ============================================================================
# Report Types API Tests
# ============================================================================


class TestReportTypesAPI:
    """Tests for /api/reports/types endpoint."""

    @pytest.mark.asyncio
    async def test_get_report_types(self, client):
        """Test getting available report types."""
        response = await client.get("/api/reports/types")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        report_types = data["data"]["report_types"]
        assert len(report_types) == 3

        type_ids = [t["id"] for t in report_types]
        assert "batch_summary" in type_ids
        assert "period_stats" in type_ids
        assert "step_analysis" in type_ids

    @pytest.mark.asyncio
    async def test_get_export_formats(self, client):
        """Test getting available export formats."""
        response = await client.get("/api/reports/types")

        assert response.status_code == 200
        data = response.json()

        export_formats = data["data"]["export_formats"]
        assert len(export_formats) >= 4

        format_ids = [f["id"] for f in export_formats]
        assert "json" in format_ids
        assert "csv" in format_ids
        assert "xlsx" in format_ids
        assert "pdf" in format_ids
