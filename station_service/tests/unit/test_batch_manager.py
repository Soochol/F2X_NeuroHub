"""
Unit tests for the BatchManager class.

Tests batch lifecycle management, command routing, and event handling.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from station_service.batch.manager import BatchManager
from station_service.core.events import Event, EventEmitter, EventType
from station_service.core.exceptions import (
    BatchAlreadyRunningError,
    BatchNotFoundError,
    BatchNotRunningError,
)
from station_service.models.config import BatchConfig, StationConfig


class TestBatchManager:
    """Test suite for BatchManager."""

    @pytest.fixture
    def event_emitter(self) -> EventEmitter:
        """Create a fresh event emitter."""
        return EventEmitter()

    @pytest.fixture
    def mock_ipc_server(self) -> MagicMock:
        """Create a mock IPC server."""
        mock = MagicMock()
        mock.router_address = "tcp://127.0.0.1:5555"
        mock.sub_address = "tcp://127.0.0.1:5557"
        mock.is_running = True
        mock.is_worker_connected = MagicMock(return_value=True)
        mock.send_command = AsyncMock(
            return_value=MagicMock(
                status="ok",
                data={"status": "running"},
                error=None,
            )
        )
        mock.start = AsyncMock()
        mock.stop = AsyncMock()
        mock.wait_for_worker = AsyncMock()  # async wait for worker connection
        mock.on_event = MagicMock()
        mock.unregister_worker = MagicMock()
        return mock

    @pytest.fixture
    def batch_manager(
        self,
        station_config: StationConfig,
        mock_ipc_server: MagicMock,
        event_emitter: EventEmitter,
    ) -> BatchManager:
        """Create a batch manager with mocked dependencies."""
        return BatchManager(
            config=station_config,
            ipc_server=mock_ipc_server,
            event_emitter=event_emitter,
        )

    # ============================================================
    # Initialization Tests
    # ============================================================

    def test_init_creates_batch_configs(
        self, batch_manager: BatchManager, station_config: StationConfig
    ):
        """Test that init creates batch config mappings."""
        expected_ids = [b.id for b in station_config.batches]

        assert batch_manager.batch_ids == expected_ids

    def test_init_sets_not_running(self, batch_manager: BatchManager):
        """Test that manager is not running after init."""
        assert batch_manager.is_running is False

    def test_running_batch_ids_initially_empty(self, batch_manager: BatchManager):
        """Test that no batches are running initially."""
        assert batch_manager.running_batch_ids == []

    # ============================================================
    # Start/Stop Manager Tests
    # ============================================================

    @pytest.mark.asyncio
    async def test_start_sets_running_flag(self, batch_manager: BatchManager):
        """Test that start() sets the running flag."""
        await batch_manager.start()

        assert batch_manager.is_running is True

        await batch_manager.stop()

    @pytest.mark.asyncio
    async def test_start_registers_event_handler(
        self, batch_manager: BatchManager, mock_ipc_server: MagicMock
    ):
        """Test that start() registers IPC event handler."""
        await batch_manager.start()

        mock_ipc_server.on_event.assert_called_once()

        await batch_manager.stop()

    @pytest.mark.asyncio
    async def test_start_when_already_running(self, batch_manager: BatchManager):
        """Test that start() is idempotent."""
        await batch_manager.start()
        await batch_manager.start()  # Should not raise

        assert batch_manager.is_running is True

        await batch_manager.stop()

    @pytest.mark.asyncio
    async def test_stop_clears_running_flag(self, batch_manager: BatchManager):
        """Test that stop() clears the running flag."""
        await batch_manager.start()
        await batch_manager.stop()

        assert batch_manager.is_running is False

    @pytest.mark.asyncio
    async def test_stop_when_not_running(self, batch_manager: BatchManager):
        """Test that stop() is idempotent."""
        await batch_manager.stop()  # Should not raise

        assert batch_manager.is_running is False

    # ============================================================
    # Start Batch Tests
    # ============================================================

    @pytest.mark.asyncio
    async def test_start_batch_creates_process(
        self, batch_manager: BatchManager, batch_config: BatchConfig
    ):
        """Test that start_batch() creates a batch process."""
        await batch_manager.start()

        with patch(
            "station_service.batch.manager.BatchProcess"
        ) as MockBatchProcess:
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_process.start = AsyncMock()
            MockBatchProcess.return_value = mock_process

            result = await batch_manager.start_batch(batch_config.id)

            assert result == mock_process
            mock_process.start.assert_called_once()

        await batch_manager.stop()

    @pytest.mark.asyncio
    async def test_start_batch_emits_event(
        self, batch_manager: BatchManager, batch_config: BatchConfig, event_emitter: EventEmitter
    ):
        """Test that start_batch() emits BATCH_STARTED event."""
        handler = AsyncMock()
        event_emitter.on(EventType.BATCH_STARTED, handler)

        await batch_manager.start()

        with patch(
            "station_service.batch.manager.BatchProcess"
        ) as MockBatchProcess:
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_process.start = AsyncMock()
            MockBatchProcess.return_value = mock_process

            await batch_manager.start_batch(batch_config.id)

        # Verify event was emitted
        handler.assert_called_once()
        event = handler.call_args[0][0]
        assert event.type == EventType.BATCH_STARTED
        assert event.batch_id == batch_config.id

        await batch_manager.stop()

    @pytest.mark.asyncio
    async def test_start_batch_not_found_raises(self, batch_manager: BatchManager):
        """Test that start_batch() raises for unknown batch."""
        await batch_manager.start()

        with pytest.raises(BatchNotFoundError):
            await batch_manager.start_batch("nonexistent_batch")

        await batch_manager.stop()

    @pytest.mark.asyncio
    async def test_start_batch_already_running_raises(
        self, batch_manager: BatchManager, batch_config: BatchConfig
    ):
        """Test that start_batch() raises if batch already running."""
        await batch_manager.start()

        with patch(
            "station_service.batch.manager.BatchProcess"
        ) as MockBatchProcess:
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_process.start = AsyncMock()
            MockBatchProcess.return_value = mock_process

            await batch_manager.start_batch(batch_config.id)

            with pytest.raises(BatchAlreadyRunningError):
                await batch_manager.start_batch(batch_config.id)

        await batch_manager.stop()

    # ============================================================
    # Stop Batch Tests
    # ============================================================

    @pytest.mark.asyncio
    async def test_stop_batch_not_running_raises(
        self, batch_manager: BatchManager, batch_config: BatchConfig
    ):
        """Test that stop_batch() raises if batch not running."""
        await batch_manager.start()

        with pytest.raises(BatchNotRunningError):
            await batch_manager.stop_batch(batch_config.id)

        await batch_manager.stop()

    @pytest.mark.asyncio
    async def test_stop_batch_emits_event(
        self, batch_manager: BatchManager, batch_config: BatchConfig, event_emitter: EventEmitter
    ):
        """Test that stop_batch() emits BATCH_STOPPED event."""
        handler = AsyncMock()
        event_emitter.on(EventType.BATCH_STOPPED, handler)

        await batch_manager.start()

        with patch(
            "station_service.batch.manager.BatchProcess"
        ) as MockBatchProcess:
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_process.start = AsyncMock()
            mock_process.stop = AsyncMock()
            mock_process.is_alive = True
            MockBatchProcess.return_value = mock_process

            await batch_manager.start_batch(batch_config.id)
            await batch_manager.stop_batch(batch_config.id)

        # Check event was emitted
        handler.assert_called_once()
        event = handler.call_args[0][0]
        assert event.type == EventType.BATCH_STOPPED
        assert event.batch_id == batch_config.id

        await batch_manager.stop()

    # ============================================================
    # Get Status Tests
    # ============================================================

    @pytest.mark.asyncio
    async def test_get_batch_status_not_found_raises(self, batch_manager: BatchManager):
        """Test that get_batch_status() raises for unknown batch."""
        await batch_manager.start()

        with pytest.raises(BatchNotFoundError):
            await batch_manager.get_batch_status("nonexistent")

        await batch_manager.stop()

    @pytest.mark.asyncio
    async def test_get_batch_status_idle(
        self, batch_manager: BatchManager, batch_config: BatchConfig
    ):
        """Test get_batch_status() for idle batch."""
        await batch_manager.start()

        status = await batch_manager.get_batch_status(batch_config.id)

        assert status["id"] == batch_config.id
        assert status["status"] == "idle"
        assert status["pid"] is None

        await batch_manager.stop()

    @pytest.mark.asyncio
    async def test_get_all_batch_statuses(
        self, batch_manager: BatchManager, batch_config: BatchConfig
    ):
        """Test get_all_batch_statuses() returns all batches."""
        await batch_manager.start()

        statuses = await batch_manager.get_all_batch_statuses()

        assert len(statuses) == 1
        assert statuses[0]["id"] == batch_config.id

        await batch_manager.stop()

    # ============================================================
    # Sequence Control Tests
    # ============================================================

    @pytest.mark.asyncio
    async def test_start_sequence_not_running_raises(
        self, batch_manager: BatchManager, batch_config: BatchConfig
    ):
        """Test that start_sequence() raises if batch not running."""
        await batch_manager.start()

        with pytest.raises(BatchNotRunningError):
            await batch_manager.start_sequence(batch_config.id)

        await batch_manager.stop()

    @pytest.mark.asyncio
    async def test_stop_sequence_not_running_raises(
        self, batch_manager: BatchManager, batch_config: BatchConfig
    ):
        """Test that stop_sequence() raises if batch not running."""
        await batch_manager.start()

        with pytest.raises(BatchNotRunningError):
            await batch_manager.stop_sequence(batch_config.id)

        await batch_manager.stop()

    # ============================================================
    # Restart Tests
    # ============================================================

    @pytest.mark.asyncio
    async def test_restart_batch_stops_and_starts(
        self, batch_manager: BatchManager, batch_config: BatchConfig
    ):
        """Test that restart_batch() stops then starts the batch."""
        await batch_manager.start()

        with patch(
            "station_service.batch.manager.BatchProcess"
        ) as MockBatchProcess:
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_process.start = AsyncMock()
            mock_process.stop = AsyncMock()
            mock_process.is_alive = True
            MockBatchProcess.return_value = mock_process

            # Start first
            await batch_manager.start_batch(batch_config.id)

            # Restart
            result = await batch_manager.restart_batch(batch_config.id)

            # Should have called stop and start
            assert mock_process.stop.called
            assert result is not None

        await batch_manager.stop()
