"""
Unit tests for WIP ViewModels.

Tests WIPGenerationViewModel, WIPScanViewModel, and WIPDashboardViewModel.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from PySide6.QtCore import QTimer

from viewmodels.wip_generation_viewmodel import (
    WIPGenerationViewModel,
    WIPGenerationWorker
)
from viewmodels.wip_scan_viewmodel import WIPScanViewModel
from viewmodels.wip_dashboard_viewmodel import WIPDashboardViewModel


class TestWIPGenerationViewModel:
    """Test WIPGenerationViewModel class."""

    @pytest.fixture
    def mock_api_client(self):
        """Mock API client."""
        return Mock()

    @pytest.fixture
    def mock_print_service(self):
        """Mock print service."""
        return Mock()

    @pytest.fixture
    def viewmodel(self, mock_api_client, mock_print_service):
        """Create WIPGenerationViewModel instance."""
        return WIPGenerationViewModel(mock_api_client, mock_print_service)

    def test_init(self, viewmodel, mock_api_client, mock_print_service):
        """Test initialization."""
        assert viewmodel.api_client == mock_api_client
        assert viewmodel.print_service == mock_print_service
        assert viewmodel.worker is None
        assert viewmodel.current_lots == []

    def test_load_lots_success(self, viewmodel, mock_api_client):
        """Test successful LOT loading."""
        # Setup mock
        mock_lots = [
            {"id": 1, "lot_number": "WF-KR-251110D-001", "status": "CREATED"},
            {"id": 2, "lot_number": "WF-KR-251110D-002", "status": "CREATED"}
        ]
        mock_api_client.get_lots.return_value = mock_lots

        # Capture signal
        signal_data = []
        viewmodel.lots_loaded.connect(lambda lots: signal_data.append(lots))

        # Execute
        viewmodel.load_lots(status="CREATED")

        # Verify
        assert viewmodel.current_lots == mock_lots
        assert signal_data == [mock_lots]
        mock_api_client.get_lots.assert_called_once_with(status="CREATED")

    def test_load_lots_error(self, viewmodel, mock_api_client):
        """Test LOT loading with error."""
        # Setup mock to raise exception
        mock_api_client.get_lots.side_effect = Exception("Network error")

        # Capture error signal
        error_msgs = []
        viewmodel.error_occurred.connect(lambda msg: error_msgs.append(msg))

        # Execute
        viewmodel.load_lots()

        # Verify
        assert len(error_msgs) == 1
        assert "조회 실패" in error_msgs[0]

    def test_start_wip_generation(self, viewmodel, mock_api_client):
        """Test starting WIP generation."""
        # Capture signal
        started = []
        viewmodel.wip_generation_started.connect(lambda: started.append(True))

        # Execute
        viewmodel.start_wip_generation(lot_id=123)

        # Verify
        assert started == [True]
        assert viewmodel.worker is not None
        assert isinstance(viewmodel.worker, WIPGenerationWorker)

    def test_start_wip_generation_already_running(self, viewmodel):
        """Test starting generation when already in progress."""
        # Create mock worker that's already running
        mock_worker = Mock()
        mock_worker.isRunning.return_value = True
        viewmodel.worker = mock_worker

        # Capture signal
        started = []
        viewmodel.wip_generation_started.connect(lambda: started.append(True))

        # Execute
        viewmodel.start_wip_generation(lot_id=123)

        # Verify - should not emit signal or create new worker
        assert started == []
        assert viewmodel.worker == mock_worker

    def test_get_lot_by_id_found(self, viewmodel):
        """Test getting LOT by ID when found."""
        viewmodel.current_lots = [
            {"id": 1, "lot_number": "WF-KR-251110D-001"},
            {"id": 2, "lot_number": "WF-KR-251110D-002"}
        ]

        lot = viewmodel.get_lot_by_id(2)

        assert lot is not None
        assert lot["id"] == 2
        assert lot["lot_number"] == "WF-KR-251110D-002"

    def test_get_lot_by_id_not_found(self, viewmodel):
        """Test getting LOT by ID when not found."""
        viewmodel.current_lots = [
            {"id": 1, "lot_number": "WF-KR-251110D-001"}
        ]

        lot = viewmodel.get_lot_by_id(999)

        assert lot is None

    def test_cleanup(self, viewmodel):
        """Test cleanup with running worker."""
        # Create mock running worker
        mock_worker = Mock()
        mock_worker.isRunning.return_value = True
        viewmodel.worker = mock_worker

        # Execute cleanup
        viewmodel.cleanup()

        # Verify
        mock_worker.terminate.assert_called_once()
        mock_worker.wait.assert_called_once_with(3000)

    def test_on_progress(self, viewmodel):
        """Test progress signal handling."""
        # Capture progress signal
        progress_data = []
        viewmodel.wip_generation_progress.connect(
            lambda pct, msg: progress_data.append((pct, msg))
        )

        # Trigger progress
        viewmodel._on_progress(50, "Test message")

        # Verify
        assert progress_data == [(50, "Test message")]

    def test_on_finished(self, viewmodel, mock_api_client):
        """Test finished signal handling."""
        # Setup mock for reload
        mock_api_client.get_lots.return_value = []

        # Capture completed signal
        result_data = []
        viewmodel.wip_generation_completed.connect(
            lambda result: result_data.append(result)
        )

        # Trigger finished
        test_result = {"generated_serials": [{"serial_number": "KR01PSA2511001"}]}
        viewmodel._on_finished(test_result)

        # Verify
        assert result_data == [test_result]
        # Should reload LOT list
        mock_api_client.get_lots.assert_called_once_with(status="CREATED")

    def test_on_error(self, viewmodel):
        """Test error signal handling."""
        # Capture error signal
        error_msgs = []
        viewmodel.error_occurred.connect(lambda msg: error_msgs.append(msg))

        # Trigger error
        viewmodel._on_error("Test error")

        # Verify
        assert error_msgs == ["Test error"]


class TestWIPGenerationWorker:
    """Test WIPGenerationWorker class."""

    @pytest.fixture
    def mock_api_client(self):
        """Mock API client."""
        return Mock()

    @pytest.fixture
    def mock_print_service(self):
        """Mock print service."""
        mock = Mock()
        mock.print_label.return_value = True
        return mock

    def test_init(self, mock_api_client):
        """Test worker initialization."""
        worker = WIPGenerationWorker(mock_api_client, lot_id=123)

        assert worker.api_client == mock_api_client
        assert worker.lot_id == 123
        assert worker.print_service is None

    def test_run_success_no_printing(self, mock_api_client, qtbot):
        """Test worker execution without printing."""
        # Setup mock
        mock_api_client.start_wip_generation.return_value = {
            "generated_serials": [
                {"serial_number": "KR01PSA2511001", "lot_number": "WF-KR-251110D-001"}
            ]
        }

        worker = WIPGenerationWorker(mock_api_client, lot_id=123, print_service=None)

        # Capture signals
        progress_data = []
        finished_data = []

        worker.progress.connect(lambda pct, msg: progress_data.append((pct, msg)))
        worker.finished.connect(lambda result: finished_data.append(result))

        # Execute
        worker.run()

        # Verify
        assert len(progress_data) >= 2  # At least initial and completion
        assert progress_data[-1][0] == 100  # Last should be 100%
        assert len(finished_data) == 1
        mock_api_client.start_wip_generation.assert_called_once_with(123)

    def test_run_success_with_printing(self, mock_api_client, mock_print_service, qtbot):
        """Test worker execution with printing."""
        # Setup mock
        mock_api_client.start_wip_generation.return_value = {
            "generated_serials": [
                {"serial_number": "KR01PSA2511001", "lot_number": "WF-KR-251110D-001"},
                {"serial_number": "KR01PSA2511002", "lot_number": "WF-KR-251110D-001"}
            ]
        }

        worker = WIPGenerationWorker(mock_api_client, lot_id=123, print_service=mock_print_service)

        # Capture signals
        progress_data = []
        worker.progress.connect(lambda pct, msg: progress_data.append((pct, msg)))

        # Execute
        worker.run()

        # Verify printing was called
        assert mock_print_service.print_label.call_count == 2
        # Verify progress updates
        assert any(pct >= 50 for pct, _ in progress_data)  # Printing progress

    def test_run_no_serials_generated(self, mock_api_client, qtbot):
        """Test worker when no serials are generated."""
        # Setup mock to return empty result
        mock_api_client.start_wip_generation.return_value = {
            "generated_serials": []
        }

        worker = WIPGenerationWorker(mock_api_client, lot_id=123)

        # Capture error signal
        error_msgs = []
        worker.error.connect(lambda msg: error_msgs.append(msg))

        # Execute
        worker.run()

        # Verify
        assert len(error_msgs) == 1
        assert "없습니다" in error_msgs[0]

    def test_run_api_error(self, mock_api_client, qtbot):
        """Test worker with API error."""
        # Setup mock to raise exception
        mock_api_client.start_wip_generation.side_effect = Exception("API Error")

        worker = WIPGenerationWorker(mock_api_client, lot_id=123)

        # Capture error signal
        error_msgs = []
        worker.error.connect(lambda msg: error_msgs.append(msg))

        # Execute
        worker.run()

        # Verify
        assert len(error_msgs) == 1
        assert "실패" in error_msgs[0]


class TestWIPScanViewModel:
    """Test WIPScanViewModel class."""

    @pytest.fixture
    def mock_api_client(self):
        """Mock API client."""
        return Mock()

    @pytest.fixture
    def viewmodel(self, mock_api_client):
        """Create WIPScanViewModel instance."""
        return WIPScanViewModel(mock_api_client)

    def test_init(self, viewmodel, mock_api_client):
        """Test initialization."""
        assert viewmodel.api_client == mock_api_client
        assert viewmodel.scan_history == []
        assert viewmodel.current_wip is None

    @patch('viewmodels.wip_scan_viewmodel.validate_serial')
    def test_scan_wip_success(self, mock_validate, viewmodel, mock_api_client):
        """Test successful WIP scanning."""
        # Setup mocks
        mock_validate.return_value = True
        mock_wip_info = {
            "serial_number": "KR01PSA2511001",
            "lot_number": "WF-KR-251110D-001",
            "product_name": "Product A",
            "current_process": "Assembly"
        }
        mock_api_client.scan_wip.return_value = mock_wip_info

        # Capture signals
        scanned_data = []
        history_data = []
        viewmodel.wip_scanned.connect(lambda data: scanned_data.append(data))
        viewmodel.scan_history_updated.connect(lambda history: history_data.append(history))

        # Execute
        viewmodel.scan_wip("KR01PSA2511001")

        # Verify
        assert scanned_data == [mock_wip_info]
        assert viewmodel.current_wip == mock_wip_info
        assert len(viewmodel.scan_history) == 1
        assert viewmodel.scan_history[0]["wip_id"] == "KR01PSA2511001"
        assert viewmodel.scan_history[0]["success"] is True
        mock_validate.assert_called_once_with("KR01PSA2511001")
        mock_api_client.scan_wip.assert_called_once_with("KR01PSA2511001")

    @patch('viewmodels.wip_scan_viewmodel.validate_serial')
    def test_scan_wip_invalid_format(self, mock_validate, viewmodel):
        """Test WIP scanning with invalid format."""
        # Setup mock
        mock_validate.return_value = False

        # Capture error signal
        error_msgs = []
        viewmodel.error_occurred.connect(lambda msg: error_msgs.append(msg))

        # Execute
        viewmodel.scan_wip("INVALID")

        # Verify
        assert len(error_msgs) == 1
        assert "형식" in error_msgs[0]
        assert viewmodel.current_wip is None

    @patch('viewmodels.wip_scan_viewmodel.validate_serial')
    def test_scan_wip_api_error(self, mock_validate, viewmodel, mock_api_client):
        """Test WIP scanning with API error."""
        # Setup mocks
        mock_validate.return_value = True
        mock_api_client.scan_wip.side_effect = Exception("Network error")

        # Capture signals
        error_msgs = []
        history_data = []
        viewmodel.error_occurred.connect(lambda msg: error_msgs.append(msg))
        viewmodel.scan_history_updated.connect(lambda history: history_data.append(history))

        # Execute
        viewmodel.scan_wip("KR01PSA2511001")

        # Verify
        assert len(error_msgs) == 1
        assert "실패" in error_msgs[0]
        # Should add to history as failure
        assert len(viewmodel.scan_history) == 1
        assert viewmodel.scan_history[0]["success"] is False

    def test_add_to_history_success(self, viewmodel):
        """Test adding successful scan to history."""
        wip_info = {
            "serial_number": "KR01PSA2511001",
            "lot_number": "WF-KR-251110D-001",
            "product_name": "Product A",
            "current_process": "Assembly"
        }

        # Capture signal
        history_data = []
        viewmodel.scan_history_updated.connect(lambda history: history_data.append(history))

        # Execute
        viewmodel._add_to_history("KR01PSA2511001", wip_info, success=True)

        # Verify
        assert len(viewmodel.scan_history) == 1
        entry = viewmodel.scan_history[0]
        assert entry["wip_id"] == "KR01PSA2511001"
        assert entry["success"] is True
        assert entry["lot_number"] == "WF-KR-251110D-001"
        assert "timestamp" in entry

    def test_add_to_history_failure(self, viewmodel):
        """Test adding failed scan to history."""
        # Execute
        viewmodel._add_to_history("INVALID", None, success=False, error="Invalid format")

        # Verify
        assert len(viewmodel.scan_history) == 1
        entry = viewmodel.scan_history[0]
        assert entry["wip_id"] == "INVALID"
        assert entry["success"] is False
        assert entry["error"] == "Invalid format"

    def test_add_to_history_limit(self, viewmodel):
        """Test history limit (max 50 entries)."""
        # Add 60 entries
        for i in range(60):
            viewmodel._add_to_history(f"SERIAL{i:03d}", None, success=True)

        # Verify only 50 kept
        assert len(viewmodel.scan_history) == 50
        # Most recent should be first
        assert viewmodel.scan_history[0]["wip_id"] == "SERIAL059"

    def test_clear_history(self, viewmodel):
        """Test clearing scan history."""
        # Add some history
        viewmodel._add_to_history("TEST001", None, success=True)
        viewmodel._add_to_history("TEST002", None, success=True)
        assert len(viewmodel.scan_history) == 2

        # Capture signal
        history_data = []
        viewmodel.scan_history_updated.connect(lambda history: history_data.append(history))

        # Clear
        viewmodel.clear_history()

        # Verify
        assert len(viewmodel.scan_history) == 0
        assert history_data == [[]]

    def test_get_current_wip(self, viewmodel):
        """Test getting current WIP."""
        # Initially None
        assert viewmodel.get_current_wip() is None

        # Set current WIP
        wip_info = {"serial_number": "KR01PSA2511001"}
        viewmodel.current_wip = wip_info

        # Verify
        assert viewmodel.get_current_wip() == wip_info

    def test_cleanup(self, viewmodel):
        """Test cleanup."""
        viewmodel.current_wip = {"serial_number": "TEST"}
        viewmodel.cleanup()

        assert viewmodel.current_wip is None


class TestWIPDashboardViewModel:
    """Test WIPDashboardViewModel class."""

    @pytest.fixture
    def mock_api_client(self):
        """Mock API client."""
        return Mock()

    @pytest.fixture
    def viewmodel(self, mock_api_client):
        """Create WIPDashboardViewModel instance."""
        return WIPDashboardViewModel(mock_api_client)

    def test_init(self, viewmodel, mock_api_client):
        """Test initialization."""
        assert viewmodel.api_client == mock_api_client
        assert viewmodel.refresh_interval == WIPDashboardViewModel.DEFAULT_REFRESH_INTERVAL
        assert viewmodel.current_statistics == {}
        assert isinstance(viewmodel.refresh_timer, QTimer)

    def test_init_custom_interval(self, mock_api_client):
        """Test initialization with custom refresh interval."""
        viewmodel = WIPDashboardViewModel(mock_api_client, refresh_interval=10000)

        assert viewmodel.refresh_interval == 10000

    def test_start_auto_refresh(self, viewmodel, mock_api_client):
        """Test starting auto-refresh."""
        # Setup mock
        mock_api_client.get_wip_statistics.return_value = {"total_wip": 0}

        # Execute
        viewmodel.start_auto_refresh()

        # Verify timer started
        assert viewmodel.refresh_timer.isActive()

    def test_stop_auto_refresh(self, viewmodel):
        """Test stopping auto-refresh."""
        # Start first
        viewmodel.refresh_timer.start(1000)
        assert viewmodel.refresh_timer.isActive()

        # Stop
        viewmodel.stop_auto_refresh()

        # Verify
        assert not viewmodel.refresh_timer.isActive()

    def test_set_refresh_interval_active(self, viewmodel):
        """Test setting refresh interval while timer is active."""
        # Start timer
        viewmodel.refresh_timer.start(30000)

        # Change interval
        viewmodel.set_refresh_interval(10000)

        # Verify
        assert viewmodel.refresh_interval == 10000
        assert viewmodel.refresh_timer.interval() == 10000

    def test_set_refresh_interval_inactive(self, viewmodel):
        """Test setting refresh interval while timer is inactive."""
        # Change interval without starting timer
        viewmodel.set_refresh_interval(15000)

        # Verify
        assert viewmodel.refresh_interval == 15000
        # Timer should not be started
        assert not viewmodel.refresh_timer.isActive()

    def test_refresh_statistics_success(self, viewmodel, mock_api_client):
        """Test successful statistics refresh."""
        # Setup mock
        mock_stats = {
            "total_wip": 100,
            "by_process": {"Assembly": 50, "Testing": 50},
            "by_lot": [],
            "alerts": []
        }
        mock_api_client.get_wip_statistics.return_value = mock_stats

        # Capture signal
        stats_data = []
        viewmodel.statistics_updated.connect(lambda stats: stats_data.append(stats))

        # Execute
        viewmodel.refresh_statistics()

        # Verify
        assert viewmodel.current_statistics == mock_stats
        assert stats_data == [mock_stats]
        mock_api_client.get_wip_statistics.assert_called_once()

    def test_refresh_statistics_error(self, viewmodel, mock_api_client):
        """Test statistics refresh with error."""
        # Setup mock to raise exception
        mock_api_client.get_wip_statistics.side_effect = Exception("API Error")

        # Capture error signal
        error_msgs = []
        viewmodel.error_occurred.connect(lambda msg: error_msgs.append(msg))

        # Execute
        viewmodel.refresh_statistics()

        # Verify
        assert len(error_msgs) == 1
        assert "실패" in error_msgs[0]

    def test_get_process_wip_counts(self, viewmodel):
        """Test getting WIP counts by process."""
        viewmodel.current_statistics = {
            "by_process": {"Assembly": 30, "Testing": 20, "Packaging": 10}
        }

        counts = viewmodel.get_process_wip_counts()

        assert len(counts) == 3
        assert ("Assembly", 30) in counts
        assert ("Testing", 20) in counts
        assert ("Packaging", 10) in counts

    def test_get_lot_progress(self, viewmodel):
        """Test getting LOT progress."""
        mock_lot_data = [
            {"lot_number": "WF-KR-251110D-001", "total_quantity": 100, "completed_quantity": 50}
        ]
        viewmodel.current_statistics = {"by_lot": mock_lot_data}

        progress = viewmodel.get_lot_progress()

        assert progress == mock_lot_data

    def test_get_alerts(self, viewmodel):
        """Test getting alerts."""
        mock_alerts = [
            {"wip_id": "KR01PSA2511001", "reason": "Stuck in process"}
        ]
        viewmodel.current_statistics = {"alerts": mock_alerts}

        alerts = viewmodel.get_alerts()

        assert alerts == mock_alerts

    def test_get_total_wip(self, viewmodel):
        """Test getting total WIP count."""
        viewmodel.current_statistics = {"total_wip": 150}

        total = viewmodel.get_total_wip()

        assert total == 150

    def test_get_total_wip_empty(self, viewmodel):
        """Test getting total WIP when no data."""
        total = viewmodel.get_total_wip()

        assert total == 0

    def test_cleanup(self, viewmodel):
        """Test cleanup."""
        # Start timer
        viewmodel.refresh_timer.start(1000)
        assert viewmodel.refresh_timer.isActive()

        # Cleanup
        viewmodel.cleanup()

        # Verify timer stopped
        assert not viewmodel.refresh_timer.isActive()


# Parametrized tests
@pytest.mark.parametrize("status,expected_call", [
    ("CREATED", "CREATED"),
    ("IN_PROGRESS", "IN_PROGRESS"),
    ("COMPLETED", "COMPLETED"),
])
def test_load_lots_status_parametrized(status, expected_call):
    """Parametrized test for loading LOTs with different statuses."""
    mock_api_client = Mock()
    mock_api_client.get_lots.return_value = []

    viewmodel = WIPGenerationViewModel(mock_api_client)
    viewmodel.load_lots(status=status)

    mock_api_client.get_lots.assert_called_once_with(status=expected_call)


@pytest.mark.parametrize("interval_ms", [
    5000,
    10000,
    30000,
    60000,
])
def test_refresh_interval_parametrized(interval_ms):
    """Parametrized test for different refresh intervals."""
    mock_api_client = Mock()
    viewmodel = WIPDashboardViewModel(mock_api_client, refresh_interval=interval_ms)

    assert viewmodel.refresh_interval == interval_ms


# Integration-style tests
def test_wip_scan_full_workflow():
    """Test complete WIP scan workflow."""
    mock_api_client = Mock()
    mock_api_client.scan_wip.return_value = {
        "serial_number": "KR01PSA2511001",
        "lot_number": "WF-KR-251110D-001",
        "product_name": "Product A",
        "current_process": "Assembly",
        "status": "IN_PROGRESS"
    }

    with patch('viewmodels.wip_scan_viewmodel.validate_serial', return_value=True):
        viewmodel = WIPScanViewModel(mock_api_client)

        # Capture all signals
        scanned = []
        history = []
        errors = []
        viewmodel.wip_scanned.connect(lambda data: scanned.append(data))
        viewmodel.scan_history_updated.connect(lambda h: history.append(h))
        viewmodel.error_occurred.connect(lambda msg: errors.append(msg))

        # Scan WIP
        viewmodel.scan_wip("KR01PSA2511001")

        # Verify workflow
        assert len(scanned) == 1
        assert scanned[0]["serial_number"] == "KR01PSA2511001"
        assert len(history) == 1
        assert len(history[0]) == 1
        assert history[0][0]["success"] is True
        assert len(errors) == 0
        assert viewmodel.current_wip is not None
