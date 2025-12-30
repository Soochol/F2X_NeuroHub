"""
Unit tests for system API routes.

Tests system information, health check, and sync status endpoints.
"""

import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch

from station_service.api.routes import system


class TestGetSystemInfo:
    """Tests for GET /api/system/info endpoint."""

    @pytest.mark.asyncio
    async def test_returns_system_info(self, station_config):
        """Test that system info returns correct station details."""
        mock_sync_engine = MagicMock()
        mock_sync_engine.is_running = True
        mock_sync_engine.is_connected = True

        result = await system.get_system_info(
            config=station_config,
            sync_engine=mock_sync_engine,
        )

        assert result.success is True
        assert result.data.station_id == station_config.station.id
        assert result.data.station_name == station_config.station.name
        assert result.data.version == system.SERVICE_VERSION
        assert result.data.uptime >= 0
        assert result.data.backend_connected is True

    @pytest.mark.asyncio
    async def test_backend_disconnected_status(self, station_config):
        """Test that disconnected backend is reported correctly."""
        mock_sync_engine = MagicMock()
        mock_sync_engine.is_running = True
        mock_sync_engine.is_connected = False

        result = await system.get_system_info(
            config=station_config,
            sync_engine=mock_sync_engine,
        )

        assert result.data.backend_connected is False

    @pytest.mark.asyncio
    async def test_sync_engine_not_running(self, station_config):
        """Test when sync engine is not running."""
        mock_sync_engine = MagicMock()
        mock_sync_engine.is_running = False

        result = await system.get_system_info(
            config=station_config,
            sync_engine=mock_sync_engine,
        )

        assert result.data.backend_connected is False


class TestGetHealth:
    """Tests for GET /api/system/health endpoint."""

    @pytest.mark.asyncio
    async def test_healthy_status(self):
        """Test health returns healthy when all systems ok."""
        mock_batch_manager = MagicMock()
        mock_batch_manager.running_batch_ids = []

        mock_sync_engine = MagicMock()
        mock_sync_engine.is_running = True
        mock_sync_engine.is_connected = True

        mock_database = MagicMock()
        mock_database.is_connected = True

        with patch.object(system, "_get_disk_usage", return_value=50.0):
            result = await system.get_health(
                batch_manager=mock_batch_manager,
                sync_engine=mock_sync_engine,
                database=mock_database,
            )

        assert result.success is True
        assert result.data.status == "healthy"
        assert result.data.batches_running == 0
        assert result.data.backend_status == "connected"
        assert result.data.disk_usage == 50.0

    @pytest.mark.asyncio
    async def test_degraded_status_backend_disconnected(self):
        """Test health returns degraded when backend disconnected."""
        mock_batch_manager = MagicMock()
        mock_batch_manager.running_batch_ids = []

        mock_sync_engine = MagicMock()
        mock_sync_engine.is_running = True
        mock_sync_engine.is_connected = False

        mock_database = MagicMock()
        mock_database.is_connected = True

        with patch.object(system, "_get_disk_usage", return_value=50.0):
            result = await system.get_health(
                batch_manager=mock_batch_manager,
                sync_engine=mock_sync_engine,
                database=mock_database,
            )

        assert result.data.status == "degraded"
        assert result.data.backend_status == "disconnected"

    @pytest.mark.asyncio
    async def test_unhealthy_status_database_disconnected(self):
        """Test health returns unhealthy when database disconnected."""
        mock_batch_manager = MagicMock()
        mock_batch_manager.running_batch_ids = []

        mock_sync_engine = MagicMock()
        mock_sync_engine.is_running = True
        mock_sync_engine.is_connected = True

        mock_database = MagicMock()
        mock_database.is_connected = False

        with patch.object(system, "_get_disk_usage", return_value=50.0):
            result = await system.get_health(
                batch_manager=mock_batch_manager,
                sync_engine=mock_sync_engine,
                database=mock_database,
            )

        assert result.data.status == "unhealthy"

    @pytest.mark.asyncio
    async def test_unhealthy_status_high_disk_usage(self):
        """Test health returns unhealthy when disk usage > 90%."""
        mock_batch_manager = MagicMock()
        mock_batch_manager.running_batch_ids = []

        mock_sync_engine = MagicMock()
        mock_sync_engine.is_running = True
        mock_sync_engine.is_connected = True

        mock_database = MagicMock()
        mock_database.is_connected = True

        with patch.object(system, "_get_disk_usage", return_value=95.0):
            result = await system.get_health(
                batch_manager=mock_batch_manager,
                sync_engine=mock_sync_engine,
                database=mock_database,
            )

        assert result.data.status == "unhealthy"

    @pytest.mark.asyncio
    async def test_running_batches_count(self):
        """Test that running batches are counted correctly."""
        mock_batch_manager = MagicMock()
        mock_batch_manager.running_batch_ids = ["batch_1", "batch_2", "batch_3"]

        mock_sync_engine = MagicMock()
        mock_sync_engine.is_running = True
        mock_sync_engine.is_connected = True

        mock_database = MagicMock()
        mock_database.is_connected = True

        with patch.object(system, "_get_disk_usage", return_value=50.0):
            result = await system.get_health(
                batch_manager=mock_batch_manager,
                sync_engine=mock_sync_engine,
                database=mock_database,
            )

        assert result.data.batches_running == 3


class TestGetSyncStatus:
    """Tests for GET /api/system/sync-status endpoint."""

    @pytest.mark.asyncio
    async def test_returns_sync_counts(self, database):
        """Test that sync status returns correct counts."""
        mock_sync_engine = MagicMock()
        mock_sync_engine.is_running = True
        mock_sync_engine.is_connected = True
        mock_sync_engine.backend_url = "http://localhost:8000"

        # Insert some test data into sync_queue
        await database.execute(
            """
            INSERT INTO sync_queue (entity_type, entity_id, action, payload_json)
            VALUES (?, ?, ?, ?)
            """,
            ("execution", "exec_1", "create", "{}"),
        )
        await database.execute(
            """
            INSERT INTO sync_queue (entity_type, entity_id, action, payload_json, retry_count)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("execution", "exec_2", "create", "{}", 10),  # Failed item
        )

        result = await system.get_sync_status(
            sync_engine=mock_sync_engine,
            database=database,
        )

        assert result.success is True
        assert result.data.pending_count == 1  # Only pending (retry_count < 5)
        assert result.data.failed_count == 1   # Only failed (retry_count >= 5)
        assert result.data.backend_connected is True
        assert result.data.backend_url == "http://localhost:8000"

    @pytest.mark.asyncio
    async def test_empty_sync_queue(self, database):
        """Test sync status with empty queue."""
        mock_sync_engine = MagicMock()
        mock_sync_engine.is_running = True
        mock_sync_engine.is_connected = False
        mock_sync_engine.backend_url = "http://localhost:8000"

        result = await system.get_sync_status(
            sync_engine=mock_sync_engine,
            database=database,
        )

        assert result.data.pending_count == 0
        assert result.data.failed_count == 0
        assert result.data.backend_connected is False


class TestForceSync:
    """Tests for POST /api/system/sync/force endpoint."""

    @pytest.mark.asyncio
    async def test_force_sync_success(self):
        """Test forcing sync returns success counts."""
        mock_sync_engine = MagicMock()
        mock_sync_engine.is_running = True
        mock_sync_engine.force_sync = AsyncMock(return_value={"success": 5, "failed": 2})

        result = await system.force_sync(sync_engine=mock_sync_engine)

        assert result.success is True
        assert result.data["success"] == 5
        assert result.data["failed"] == 2
        mock_sync_engine.force_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_force_sync_engine_not_running(self):
        """Test force sync raises when engine not running."""
        from fastapi import HTTPException

        mock_sync_engine = MagicMock()
        mock_sync_engine.is_running = False

        with pytest.raises(HTTPException) as exc_info:
            await system.force_sync(sync_engine=mock_sync_engine)

        assert exc_info.value.status_code == 503


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_determine_health_status_healthy(self):
        """Test healthy status determination."""
        status = system._determine_health_status(
            database_connected=True,
            backend_connected=True,
            disk_usage=50.0,
        )
        assert status == "healthy"

    def test_determine_health_status_degraded_backend(self):
        """Test degraded status when backend disconnected."""
        status = system._determine_health_status(
            database_connected=True,
            backend_connected=False,
            disk_usage=50.0,
        )
        assert status == "degraded"

    def test_determine_health_status_degraded_disk(self):
        """Test degraded status when disk usage 80-90%."""
        status = system._determine_health_status(
            database_connected=True,
            backend_connected=True,
            disk_usage=85.0,
        )
        assert status == "degraded"

    def test_determine_health_status_unhealthy_database(self):
        """Test unhealthy status when database disconnected."""
        status = system._determine_health_status(
            database_connected=False,
            backend_connected=True,
            disk_usage=50.0,
        )
        assert status == "unhealthy"

    def test_determine_health_status_unhealthy_disk(self):
        """Test unhealthy status when disk usage > 90%."""
        status = system._determine_health_status(
            database_connected=True,
            backend_connected=True,
            disk_usage=95.0,
        )
        assert status == "unhealthy"

    def test_get_disk_usage_returns_float(self):
        """Test disk usage returns a valid percentage."""
        usage = system._get_disk_usage()
        assert isinstance(usage, float)
        assert 0.0 <= usage <= 100.0
