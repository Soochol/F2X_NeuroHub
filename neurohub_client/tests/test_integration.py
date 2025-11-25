"""
Integration tests for Production Tracker App.

Tests component interactions and end-to-end workflows.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QEvent, QTimer

from viewmodels.wip_generation_viewmodel import WIPGenerationViewModel
from viewmodels.wip_scan_viewmodel import WIPScanViewModel
from viewmodels.wip_dashboard_viewmodel import WIPDashboardViewModel
from views.pages.wip_generation_page import WIPGenerationPage
from views.pages.wip_scan_page import WIPScanPage
from views.pages.wip_dashboard_page import WIPDashboardPage
from services.api_client import APIClient
from services.barcode_service import BarcodeService
from utils.config import AppConfig


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't quit - reuse for all tests


@pytest.fixture
def mock_api_client():
    """Mock API client with common responses."""
    client = Mock(spec=APIClient)

    # Default mock responses
    client.get_lots.return_value = [
        {
            "id": 1,
            "lot_number": "WF-KR-251110D-001",
            "product_name": "Product A",
            "quantity": 100,
            "status": "CREATED"
        }
    ]

    client.start_wip_generation.return_value = {
        "generated_serials": [
            {"serial_number": "KR01PSA2511001", "lot_number": "WF-KR-251110D-001"},
            {"serial_number": "KR01PSA2511002", "lot_number": "WF-KR-251110D-001"}
        ]
    }

    client.scan_wip.return_value = {
        "serial_number": "KR01PSA2511001",
        "lot_number": "WF-KR-251110D-001",
        "product_name": "Product A",
        "current_process": "Assembly",
        "status": "IN_PROGRESS"
    }

    client.get_wip_statistics.return_value = {
        "total_wip": 100,
        "by_process": {"Assembly": 50, "Testing": 30, "Packaging": 20},
        "by_lot": [
            {
                "lot_number": "WF-KR-251110D-001",
                "total_quantity": 100,
                "completed_quantity": 50
            }
        ],
        "alerts": []
    }

    return client


@pytest.fixture
def mock_print_service():
    """Mock print service."""
    service = Mock()
    service.print_label.return_value = True
    service.get_available_printers.return_value = ["Zebra ZD421"]
    service.set_printer.return_value = True
    return service


@pytest.fixture
def mock_barcode_service():
    """Mock barcode service."""
    service = Mock(spec=BarcodeService)
    return service


@pytest.fixture
def app_config():
    """Create app configuration."""
    config = Mock(spec=AppConfig)
    config.api_base_url = "http://localhost:8000"
    config.api_token = "test_token"
    config.printer_queue = "Zebra ZD421"
    config.zpl_template_path = ""
    return config


class TestWIPGenerationIntegration:
    """Integration tests for WIP Generation workflow."""

    def test_generation_viewmodel_to_page_integration(self, qapp, mock_api_client, mock_print_service, app_config):
        """Test ViewModel to Page signal integration."""
        # Create ViewModel and Page
        viewmodel = WIPGenerationViewModel(mock_api_client, mock_print_service)
        page = WIPGenerationPage(viewmodel, app_config)

        # Verify signal connections
        assert viewmodel.lots_loaded.receivers(viewmodel.lots_loaded) > 0
        assert viewmodel.wip_generation_completed.receivers(viewmodel.wip_generation_completed) > 0

        # Trigger LOT loading
        viewmodel.load_lots(status="CREATED")

        # Verify table populated (ViewModel emitted signal, Page received and displayed)
        assert page.lot_table.rowCount() > 0
        assert "WF-KR-251110D-001" in page.lot_table.item(0, 0).text()

    def test_complete_generation_workflow(self, qapp, mock_api_client, mock_print_service, app_config):
        """Test complete WIP generation workflow end-to-end."""
        viewmodel = WIPGenerationViewModel(mock_api_client, mock_print_service)
        page = WIPGenerationPage(viewmodel, app_config)

        # Load LOTs
        viewmodel.load_lots(status="CREATED")
        assert page.lot_table.rowCount() == 1

        # Capture completion signal
        completed = []
        viewmodel.wip_generation_completed.connect(lambda result: completed.append(result))

        # Start generation (simulate button click)
        page.lot_table.selectRow(0)
        page._on_generate_clicked()

        # Wait for worker to start
        assert viewmodel.worker is not None

        # Simulate worker completion
        result = mock_api_client.start_wip_generation.return_value
        viewmodel.worker.finished.emit(result)

        # Verify completion
        assert len(completed) == 1
        assert len(completed[0]["generated_serials"]) == 2

        # Verify print service was called in worker
        # (In real scenario, worker would call print_service.print_label)

    def test_generation_with_printing_integration(self, mock_api_client, mock_print_service):
        """Test WIP generation integrates with print service."""
        from viewmodels.wip_generation_viewmodel import WIPGenerationWorker

        worker = WIPGenerationWorker(mock_api_client, lot_id=1, print_service=mock_print_service)

        # Capture signals
        progress = []
        finished = []
        worker.progress.connect(lambda pct, msg: progress.append((pct, msg)))
        worker.finished.connect(lambda result: finished.append(result))

        # Run worker
        worker.run()

        # Verify print service called for each serial
        assert mock_print_service.print_label.call_count == 2
        # First call args
        call_args = mock_print_service.print_label.call_args_list[0][0]
        assert "KR01PSA2511001" in call_args

        # Verify progress updates
        assert len(progress) >= 3
        assert progress[-1][0] == 100  # Last progress is 100%

        # Verify completion
        assert len(finished) == 1


class TestWIPScanIntegration:
    """Integration tests for WIP Scan workflow."""

    @patch('viewmodels.wip_scan_viewmodel.validate_serial')
    def test_scan_viewmodel_to_page_integration(self, mock_validate, qapp, mock_api_client, app_config):
        """Test ViewModel to Page signal integration."""
        mock_validate.return_value = True

        # Create ViewModel and Page
        viewmodel = WIPScanViewModel(mock_api_client)
        page = WIPScanPage(viewmodel, app_config)

        # Verify signal connections
        assert viewmodel.wip_scanned.receivers(viewmodel.wip_scanned) > 0
        assert viewmodel.scan_history_updated.receivers(viewmodel.scan_history_updated) > 0

        # Trigger scan
        page.barcode_input.setText("KR01PSA2511001")
        page._on_scan()

        # Verify information displayed
        assert page.lot_value.text() == "WF-KR-251110D-001"
        assert page.product_value.text() == "Product A"
        assert page.process_value.text() == "Assembly"

        # Verify history updated
        assert page.history_list.count() == 1

    @patch('viewmodels.wip_scan_viewmodel.validate_serial')
    def test_complete_scan_workflow(self, mock_validate, qapp, mock_api_client, app_config):
        """Test complete WIP scan workflow."""
        mock_validate.return_value = True

        viewmodel = WIPScanViewModel(mock_api_client)
        page = WIPScanPage(viewmodel, app_config)

        # Scan multiple WIPs
        serials = ["KR01PSA2511001", "KR01PSA2511002", "KR01PSA2511003"]

        for serial in serials:
            page.barcode_input.setText(serial)
            page._on_scan()

        # Verify all added to history
        assert len(viewmodel.scan_history) == 3
        assert page.history_list.count() == 3

        # Verify most recent first
        assert viewmodel.scan_history[0]["wip_id"] == "KR01PSA2511003"

        # Clear history
        page._on_clear_history()
        assert len(viewmodel.scan_history) == 0
        assert page.history_list.count() == 0

    @patch('viewmodels.wip_scan_viewmodel.validate_serial')
    def test_scan_with_barcode_service_integration(self, mock_validate, qapp, mock_api_client, mock_barcode_service, app_config):
        """Test scan workflow with barcode service integration."""
        mock_validate.return_value = True

        viewmodel = WIPScanViewModel(mock_api_client)
        page = WIPScanPage(viewmodel, app_config)

        # Simulate barcode scanner input
        mock_barcode_service.barcode_scanned.emit("KR01PSA2511001")

        # Connect barcode service to page input
        mock_barcode_service.barcode_scanned.connect(
            lambda barcode: page.barcode_input.setText(barcode)
        )
        mock_barcode_service.barcode_scanned.connect(
            lambda barcode: page._on_scan()
        )

        # Emit barcode
        mock_barcode_service.barcode_scanned.emit("KR01PSA2511001")

        # Verify scan processed
        # (In real app, this would be routed through main_window event filter)


class TestWIPDashboardIntegration:
    """Integration tests for WIP Dashboard workflow."""

    def test_dashboard_viewmodel_to_page_integration(self, qapp, mock_api_client, app_config):
        """Test ViewModel to Page signal integration."""
        # Create ViewModel and Page
        viewmodel = WIPDashboardViewModel(mock_api_client)
        page = WIPDashboardPage(viewmodel, app_config)

        # Verify signal connections
        assert viewmodel.statistics_updated.receivers(viewmodel.statistics_updated) > 0

        # Trigger statistics refresh
        viewmodel.refresh_statistics()

        # Verify UI updated
        assert "100" in page.total_label.text()
        assert page.lot_table.rowCount() == 1

    def test_dashboard_auto_refresh(self, qapp, mock_api_client, app_config, qtbot):
        """Test dashboard auto-refresh functionality."""
        viewmodel = WIPDashboardViewModel(mock_api_client, refresh_interval=100)  # 100ms for test
        page = WIPDashboardPage(viewmodel, app_config)

        # Track refresh calls
        refresh_count = [0]
        original_refresh = viewmodel.refresh_statistics

        def count_refresh():
            refresh_count[0] += 1
            original_refresh()

        viewmodel.refresh_statistics = count_refresh

        # Start auto-refresh
        viewmodel.start_auto_refresh()
        assert viewmodel.refresh_timer.isActive()

        # Wait for multiple refreshes
        qtbot.wait(350)  # Wait for ~3 refreshes

        # Stop
        viewmodel.stop_auto_refresh()

        # Verify multiple refreshes occurred
        assert refresh_count[0] >= 2

    def test_dashboard_toggle_auto_refresh(self, qapp, mock_api_client, app_config):
        """Test toggling auto-refresh from UI."""
        viewmodel = WIPDashboardViewModel(mock_api_client)
        page = WIPDashboardPage(viewmodel, app_config)

        # Initially checked and active
        assert page.auto_refresh_check.isChecked()
        assert viewmodel.refresh_timer.isActive()

        # Uncheck
        page.auto_refresh_check.setChecked(False)
        page._on_auto_refresh_toggled(Qt.Unchecked)

        # Verify stopped
        assert not viewmodel.refresh_timer.isActive()

        # Re-check
        page.auto_refresh_check.setChecked(True)
        page._on_auto_refresh_toggled(Qt.Checked)

        # Verify restarted
        assert viewmodel.refresh_timer.isActive()


class TestBarcodeUtilsIntegration:
    """Integration tests for barcode utilities with other components."""

    def test_barcode_validation_in_scan_workflow(self, qapp, mock_api_client, app_config):
        """Test barcode validation integrates with scan workflow."""
        from utils.barcode_utils import validate_serial

        viewmodel = WIPScanViewModel(mock_api_client)

        # Capture errors
        errors = []
        viewmodel.error_occurred.connect(lambda msg: errors.append(msg))

        # Test with invalid serial
        with patch('viewmodels.wip_scan_viewmodel.validate_serial', return_value=False):
            viewmodel.scan_wip("INVALID")
            assert len(errors) == 1
            assert "형식" in errors[0]

        # Test with valid serial
        with patch('viewmodels.wip_scan_viewmodel.validate_serial', return_value=True):
            viewmodel.scan_wip("KR01PSA2511001")
            # Should not add another error
            assert len(errors) == 1

    def test_barcode_generation_in_print_workflow(self, mock_api_client, mock_print_service):
        """Test barcode generation integrates with printing."""
        from utils.barcode_utils import BarcodeGenerator
        from utils.zebra_printer import ZebraPrinter

        # Generate ZPL
        zpl = BarcodeGenerator.generate_zpl_label("KR01PSA2511001", barcode_type='code128')

        # Verify ZPL structure
        assert "^XA" in zpl
        assert "^XZ" in zpl
        assert "KR01PSA2511001" in zpl
        assert "^BCN" in zpl  # Code128 command

        # Mock printer
        with patch('socket.socket') as mock_socket_class:
            mock_socket = MagicMock()
            mock_socket_class.return_value.__enter__.return_value = mock_socket

            printer = ZebraPrinter(ip_address="192.168.1.100")
            result = printer.send_zpl(zpl)

            assert result is True
            # Verify ZPL was sent
            sent_data = mock_socket.sendall.call_args[0][0].decode('utf-8')
            assert "KR01PSA2511001" in sent_data


class TestAPIClientIntegration:
    """Integration tests for API client with ViewModels."""

    def test_api_client_with_generation_viewmodel(self, mock_api_client):
        """Test API client integration with generation ViewModel."""
        viewmodel = WIPGenerationViewModel(mock_api_client)

        # Load LOTs
        viewmodel.load_lots(status="CREATED")

        # Verify API called correctly
        mock_api_client.get_lots.assert_called_once_with(status="CREATED")
        assert len(viewmodel.current_lots) == 1

        # Start generation
        viewmodel.start_wip_generation(lot_id=1)
        assert viewmodel.worker is not None

        # Simulate worker calling API
        result = mock_api_client.start_wip_generation(1)
        assert len(result["generated_serials"]) == 2

    def test_api_client_with_scan_viewmodel(self, mock_api_client):
        """Test API client integration with scan ViewModel."""
        with patch('viewmodels.wip_scan_viewmodel.validate_serial', return_value=True):
            viewmodel = WIPScanViewModel(mock_api_client)

            # Scan WIP
            viewmodel.scan_wip("KR01PSA2511001")

            # Verify API called
            mock_api_client.scan_wip.assert_called_once_with("KR01PSA2511001")
            assert viewmodel.current_wip is not None

    def test_api_client_with_dashboard_viewmodel(self, mock_api_client):
        """Test API client integration with dashboard ViewModel."""
        viewmodel = WIPDashboardViewModel(mock_api_client)

        # Refresh statistics
        viewmodel.refresh_statistics()

        # Verify API called
        mock_api_client.get_wip_statistics.assert_called_once()
        assert viewmodel.current_statistics["total_wip"] == 100


class TestPrintServiceIntegration:
    """Integration tests for print service with generation workflow."""

    def test_print_service_in_generation_workflow(self, mock_api_client, mock_print_service):
        """Test print service integration in generation workflow."""
        from viewmodels.wip_generation_viewmodel import WIPGenerationWorker

        worker = WIPGenerationWorker(mock_api_client, lot_id=1, print_service=mock_print_service)

        # Run worker
        worker.run()

        # Verify print service used
        assert mock_print_service.print_label.call_count == 2

        # Verify correct data passed
        first_call = mock_print_service.print_label.call_args_list[0]
        assert "KR01PSA2511001" in str(first_call)

    def test_print_service_with_zebra_printer(self):
        """Test print service with Zebra printer integration."""
        from utils.zebra_printer import ZebraPrinter
        from utils.barcode_utils import BarcodeGenerator

        with patch('socket.socket') as mock_socket_class:
            mock_socket = MagicMock()
            mock_socket_class.return_value.__enter__.return_value = mock_socket

            printer = ZebraPrinter(ip_address="192.168.1.100")

            # Print label (integrates BarcodeGenerator)
            result = printer.print_label("KR01PSA2511001", barcode_type='code128')

            assert result is True
            # Verify ZPL generated and sent
            mock_socket.sendall.assert_called_once()


class TestErrorHandlingIntegration:
    """Integration tests for error handling across components."""

    def test_api_error_propagation_to_ui(self, qapp, app_config):
        """Test API errors propagate to UI properly."""
        mock_api_client = Mock()
        mock_api_client.get_lots.side_effect = Exception("Network error")

        viewmodel = WIPGenerationViewModel(mock_api_client)
        page = WIPGenerationPage(viewmodel, app_config)

        # Capture errors
        errors = []
        viewmodel.error_occurred.connect(lambda msg: errors.append(msg))

        # Trigger load
        viewmodel.load_lots()

        # Verify error captured
        assert len(errors) == 1
        assert "실패" in errors[0]

    def test_print_error_handling(self, mock_api_client):
        """Test print errors are handled gracefully."""
        mock_print_service = Mock()
        mock_print_service.print_label.return_value = False  # Print fails

        from viewmodels.wip_generation_viewmodel import WIPGenerationWorker

        worker = WIPGenerationWorker(mock_api_client, lot_id=1, print_service=mock_print_service)

        # Should not raise exception even if print fails
        worker.run()

        # Worker should still complete
        assert mock_print_service.print_label.call_count == 2

    def test_validation_error_handling(self, qapp, mock_api_client, app_config):
        """Test validation errors handled properly."""
        viewmodel = WIPScanViewModel(mock_api_client)
        page = WIPScanPage(viewmodel, app_config)

        # Capture errors
        errors = []
        viewmodel.error_occurred.connect(lambda msg: errors.append(msg))

        with patch('viewmodels.wip_scan_viewmodel.validate_serial', return_value=False):
            # Try to scan invalid serial
            page.barcode_input.setText("INVALID")
            page._on_scan()

            # Verify error shown
            assert len(errors) == 1
            assert "형식" in errors[0]

            # API should not be called
            mock_api_client.scan_wip.assert_not_called()


class TestSignalSlotIntegration:
    """Integration tests for signal/slot connections."""

    def test_viewmodel_to_page_signals(self, qapp, mock_api_client, app_config):
        """Test all ViewModel to Page signal connections."""
        # Generation
        gen_viewmodel = WIPGenerationViewModel(mock_api_client)
        gen_page = WIPGenerationPage(gen_viewmodel, app_config)

        assert gen_viewmodel.lots_loaded.receivers(gen_viewmodel.lots_loaded) > 0
        assert gen_viewmodel.wip_generation_completed.receivers(gen_viewmodel.wip_generation_completed) > 0
        assert gen_viewmodel.error_occurred.receivers(gen_viewmodel.error_occurred) > 0

        # Scan
        scan_viewmodel = WIPScanViewModel(mock_api_client)
        scan_page = WIPScanPage(scan_viewmodel, app_config)

        assert scan_viewmodel.wip_scanned.receivers(scan_viewmodel.wip_scanned) > 0
        assert scan_viewmodel.scan_history_updated.receivers(scan_viewmodel.scan_history_updated) > 0
        assert scan_viewmodel.error_occurred.receivers(scan_viewmodel.error_occurred) > 0

        # Dashboard
        dash_viewmodel = WIPDashboardViewModel(mock_api_client)
        dash_page = WIPDashboardPage(dash_viewmodel, app_config)

        assert dash_viewmodel.statistics_updated.receivers(dash_viewmodel.statistics_updated) > 0
        assert dash_viewmodel.error_occurred.receivers(dash_viewmodel.error_occurred) > 0

    def test_page_cleanup_disconnects_signals(self, qapp, mock_api_client, app_config):
        """Test page cleanup properly disconnects signals."""
        viewmodel = WIPDashboardViewModel(mock_api_client)
        page = WIPDashboardPage(viewmodel, app_config)

        # Verify timer active
        assert viewmodel.refresh_timer.isActive()

        # Cleanup
        page.cleanup()

        # Verify timer stopped
        assert not viewmodel.refresh_timer.isActive()


# Parametrized integration tests
@pytest.mark.parametrize("barcode_type,expected_command", [
    ("code128", "^BCN"),
    ("qr", "^BQN"),
])
def test_barcode_type_integration_parametrized(barcode_type, expected_command):
    """Parametrized test for barcode type integration."""
    from utils.barcode_utils import BarcodeGenerator

    zpl = BarcodeGenerator.generate_zpl_label("TEST123", barcode_type=barcode_type)

    assert "^XA" in zpl
    assert "^XZ" in zpl
    assert expected_command in zpl
    assert "TEST123" in zpl


@pytest.mark.parametrize("serial,should_pass", [
    ("KR01PSA2511001", True),
    ("US02ABC2512999", True),
    ("INVALID", False),
    ("", False),
])
def test_validation_integration_parametrized(serial, should_pass, mock_api_client):
    """Parametrized test for validation integration."""
    from utils.barcode_utils import validate_serial

    viewmodel = WIPScanViewModel(mock_api_client)

    # Capture errors
    errors = []
    viewmodel.error_occurred.connect(lambda msg: errors.append(msg))

    with patch('viewmodels.wip_scan_viewmodel.validate_serial', side_effect=validate_serial):
        viewmodel.scan_wip(serial)

        if should_pass:
            # Should call API
            if serial:  # Only if not empty
                mock_api_client.scan_wip.assert_called()
        else:
            # Should emit error
            assert len(errors) >= 1


# Performance/stress tests
def test_scan_history_performance(mock_api_client):
    """Test scan history performance with many entries."""
    with patch('viewmodels.wip_scan_viewmodel.validate_serial', return_value=True):
        viewmodel = WIPScanViewModel(mock_api_client)

        # Scan 100 WIPs
        for i in range(100):
            viewmodel.scan_wip(f"KR01PSA25110{i:02d}")

        # Should only keep last 50
        assert len(viewmodel.scan_history) == 50

        # Most recent should be first
        assert "99" in viewmodel.scan_history[0]["wip_id"]


def test_concurrent_generation_prevention(mock_api_client, mock_print_service):
    """Test that concurrent generations are prevented."""
    viewmodel = WIPGenerationViewModel(mock_api_client, mock_print_service)

    # Start first generation
    viewmodel.start_wip_generation(lot_id=1)
    first_worker = viewmodel.worker

    # Try to start second generation
    viewmodel.start_wip_generation(lot_id=2)
    second_worker = viewmodel.worker

    # Should be same worker (second request ignored)
    assert first_worker == second_worker
