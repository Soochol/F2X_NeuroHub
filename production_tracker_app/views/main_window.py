"""
Main Window for Production Tracker App with Sidebar Navigation.
"""
import logging
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QStatusBar, QMessageBox, QPushButton, QFrame, QListWidget,
    QListWidgetItem, QStackedWidget
)
from PySide6.QtCore import Qt, QTimer, QEvent
from PySide6.QtGui import QKeyEvent

from views.pages.home_page import HomePage

from views.pages.settings_page import SettingsPage
from views.pages.help_page import HelpPage
from views.pages.wip_generation_page import WIPGenerationPage
from views.pages.wip_dashboard_page import WIPDashboardPage
from views.defect_dialog import DefectDialog
from viewmodels.wip_generation_viewmodel import WIPGenerationViewModel
from viewmodels.wip_dashboard_viewmodel import WIPDashboardViewModel
from widgets.base_components import StatusIndicator
from widgets.toast_notification import Toast
from utils.theme_manager import get_theme
from utils.process_data_generator import ProcessDataGenerator
from utils.exception_handler import (
    SignalConnector, CleanupManager, safe_slot, safe_cleanup
)
from services.barcode_service import BarcodeService

logger = logging.getLogger(__name__)
theme = get_theme()


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation."""

    def __init__(self, viewmodel, config):
        super().__init__()
        self.viewmodel = viewmodel
        self.config = config

        self.setWindowTitle(f"F2X NeuroHub - {config.process_name}")

        # Window size for sidebar layout
        self.setMinimumSize(900, 726)
        self.resize(900, 726)

        # Work state tracking
        self.current_lot = None
        self.start_time = None

        # Timer for elapsed time updates
        self.elapsed_timer = QTimer()
        self.elapsed_timer.timeout.connect(self._update_elapsed_time)

        # Barcode scanner service
        self.barcode_service = BarcodeService()
        self.barcode_service.barcode_valid.connect(self._on_lot_barcode_scanned)
        self.barcode_service.serial_valid.connect(self._on_serial_barcode_scanned)
        self.barcode_service.barcode_invalid.connect(self._on_invalid_barcode)

        self.setup_ui()
        self.connect_signals()

        # Install event filter for global barcode scanning
        self.installEventFilter(self)

        logger.info("MainWindow initialized with sidebar navigation and barcode scanner")

    def setup_ui(self):
        """Setup UI components with sidebar navigation."""
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("main_sidebar")
        sidebar.setFixedWidth(160)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Navigation list
        self.nav_list = QListWidget()
        self.nav_list.setObjectName("main_nav")
        self.nav_list.setFrameShape(QListWidget.NoFrame)

        # Add navigation items
        nav_items = [
            ("홈", "home"),

            ("설정", "settings"),
            ("도움말", "help"),
        ]

        for label, data in nav_items:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, data)
            self.nav_list.addItem(item)

        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        sidebar_layout.addWidget(self.nav_list)
        sidebar_layout.addStretch()

        main_layout.addWidget(sidebar)

        # Content area
        content_widget = QWidget()
        content_widget.setObjectName("main_content")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(16)

        # Stacked widget for pages
        self.stack = QStackedWidget()

        # Create pages
        self.home_page = HomePage(self.config)


        # Get services from viewmodel
        api_client = getattr(self.viewmodel, 'api_client', None)

        # Create WIP ViewModels
        # self.wip_generation_vm = WIPGenerationViewModel(api_client, print_service)
        # self.wip_dashboard_vm = WIPDashboardViewModel(api_client)

        # Create WIP pages
        # self.wip_generation_page = WIPGenerationPage(self.wip_generation_vm, self.config)
        # self.wip_dashboard_page = WIPDashboardPage(self.wip_dashboard_vm, self.config)

        # Create settings page
        self.settings_page = SettingsPage(self.config, api_client)
        self.help_page = HelpPage(self.config)

        # Add pages to stack
        self.stack.addWidget(self.home_page)

        # self.stack.addWidget(self.wip_generation_page)
        # self.stack.addWidget(self.wip_dashboard_page)
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.help_page)

        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("status_bar")
        self.setStatusBar(self.status_bar)

        # Connection status indicator
        self.connection_indicator = StatusIndicator("연결 중...", "warning")
        self.status_bar.addPermanentWidget(self.connection_indicator)

        # Select first item (Home)
        self.nav_list.setCurrentRow(0)

        # Apply styles
        self._apply_styles()

        # Connect page signals
        self._connect_page_signals()

    def _apply_styles(self):
        """Apply styles for sidebar navigation."""
        bg_dark = theme.get('colors.background.dark')
        bg_default = theme.get('colors.background.default')
        border = theme.get('colors.border.default')
        grey_400 = theme.get('colors.grey.400')
        grey_600 = theme.get('colors.grey.600')
        brand = theme.get('colors.brand.main')

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {bg_dark};
            }}

            #main_sidebar {{
                background-color: {bg_dark};
                border-right: 1px solid {border};
            }}

            #main_nav {{
                background-color: transparent;
                border: none;
                outline: none;
            }}

            #main_nav::item {{
                padding: 14px 16px;
                border-left: 3px solid transparent;
                color: {grey_400};
                font-size: 13px;
            }}

            #main_nav::item:selected {{
                background-color: {border};
                border-left: 3px solid {brand};
                color: {brand};
                font-weight: 600;
            }}

            #main_nav::item:hover:!selected {{
                background-color: {bg_default};
            }}

            #main_content {{
                background-color: {bg_dark};
            }}

            QStatusBar {{
                background-color: {bg_dark};
                border-top: 1px solid {border};
                color: {grey_600};
                font-size: 11px;
            }}
        """)

    def _connect_page_signals(self):
        """Connect page signals to handlers."""
        connector = SignalConnector()
        connector.connect(
            self.home_page.start_requested,
            self._on_start_work_requested,
            "start_requested -> _on_start_work_requested"
        ).connect(
            self.home_page.pass_requested,
            self._on_pass_requested,
            "pass_requested -> _on_pass_requested"
        ).connect(
            self.home_page.fail_requested,
            self._on_fail_requested,
            "fail_requested -> _on_fail_requested"
        ).connect(
            self.settings_page.settings_saved,
            self._on_settings_saved,
            "settings_saved -> _on_settings_saved"
        )

        if not connector.all_connected():
            logger.error(
                f"페이지 시그널 연결 실패: {connector.failed_connections}"
            )

    @safe_slot("설정 저장 후 처리 실패")
    def _on_settings_saved(self):
        """Handle settings saved - refresh page info."""
        self.home_page.refresh_info()


    def connect_signals(self):
        """Connect ViewModel signals to UI updates."""
        connector = SignalConnector()
        connector.connect(
            self.viewmodel.lot_updated,
            self._on_lot_updated,
            "lot_updated -> _on_lot_updated"
        ).connect(
            self.viewmodel.work_started,
            self._on_work_started,
            "work_started -> _on_work_started"
        ).connect(
            self.viewmodel.work_completed,
            self._on_work_completed,
            "work_completed -> _on_work_completed"
        ).connect(
            self.viewmodel.error_occurred,
            self._on_error,
            "error_occurred -> _on_error"
        ).connect(
            self.viewmodel.connection_status_changed,
            self._on_connection_status_changed,
            "connection_status_changed -> _on_connection_status_changed"
        ).connect(
            self.viewmodel.serial_received,
            self._on_serial_received,
            "serial_received -> _on_serial_received"
        )

        if not connector.all_connected():
            logger.error(
                f"일부 시그널 연결 실패: {connector.failed_connections}"
            )

    def _on_nav_changed(self, index):
        """Handle navigation item change."""
        item = self.nav_list.item(index)
        if not item:
            return

        page_type = item.data(Qt.UserRole)
        self.stack.setCurrentIndex(index)

        # Focus on input when switching to specific pages
        if page_type == "home":
            self.home_page.focus_input()

    def _on_start_work_requested(self, lot_number: str):
        """Handle start work request from start page (LOT-level)."""
        if not lot_number:
            Toast.warning(self, "LOT 번호를 입력하세요.")
            return

        # Disable start controls during request
        self.home_page.set_enabled(False)

        # Call viewmodel to start work (LOT-level)
        self.viewmodel.start_work(lot_number)

    def _on_serial_received(self, serial_number: str):
        """Handle serial number received (from barcode or server)."""
        # Update HomePage serial input - REMOVED as requested
        # self.home_page.set_serial_number(serial_number)
        Toast.success(self, f"Serial 스캔: {serial_number}")

    def _on_pass_requested(self):
        """Handle PASS completion request."""
        if not self.current_lot:
            Toast.warning(self, "진행 중인 작업이 없습니다.")
            return

        # Generate process data for PASS
        complete_time = datetime.now()
        process_data = ProcessDataGenerator.generate_pass_data(
            self.config.process_number,
            self.current_lot,
            self.start_time,
            complete_time
        )

        # Get worker_id from auth service
        worker_id = self.viewmodel.auth_service.get_current_user_id()

        # Build completion data
        completion_data = {
            "lot_number": self.current_lot,
            "line_id": self.config.line_id,
            "process_id": self.config.process_id,
            "process_name": self.config.process_name,
            "equipment_id": self.config.equipment_id,
            "worker_id": worker_id,
            "start_time": self.start_time.isoformat(),
            "complete_time": complete_time.isoformat(),
            "result": "PASS",
            "process_data": process_data
        }

        # Disable buttons during request
        self.home_page.set_enabled(False)

        # Call viewmodel to complete work
        self.viewmodel.complete_work(completion_data)

    def _on_fail_requested(self):
        """Handle FAIL completion request."""
        if not self.current_lot:
            Toast.warning(self, "진행 중인 작업이 없습니다.")
            return

        # Show defect dialog
        dialog = DefectDialog(self.config.process_number, self)
        if dialog.exec():
            defect_type, defect_description = dialog.get_result()

            # Generate process data for FAIL
            complete_time = datetime.now()
            process_data = ProcessDataGenerator.generate_fail_data(
                self.config.process_number,
                self.current_lot,
                self.start_time,
                complete_time,
                defect_type,
                defect_description
            )

            # Get worker_id from auth service
            worker_id = self.viewmodel.auth_service.get_current_user_id()

            # Build completion data
            completion_data = {
                "lot_number": self.current_lot,
                "line_id": self.config.line_id,
                "process_id": self.config.process_id,
                "process_name": self.config.process_name,
                "equipment_id": self.config.equipment_id,
                "worker_id": worker_id,
                "start_time": self.start_time.isoformat(),
                "complete_time": complete_time.isoformat(),
                "result": "FAIL",
                "process_data": process_data
            }

            # Disable buttons during request
            self.home_page.set_enabled(False)

            # Call viewmodel to complete work
            self.viewmodel.complete_work(completion_data)

    def _on_lot_updated(self, lot_data: dict):
        """Handle LOT information update."""
        if lot_data:
            self.current_lot = lot_data.get("lot_number")
        else:
            self.current_lot = None
            self.start_time = None

    @safe_slot("착공 처리 실패", show_dialog=True)
    def _on_work_started(self, lot_number: str):
        """Handle work started event."""
        self.current_lot = lot_number
        self.start_time = datetime.now()
        start_time_str = self.start_time.strftime("%H:%M:%S")

        # Get serial number from viewmodel (if SERIAL-level work)
        serial_number = self.viewmodel.current_serial

        # Update home page
        self.home_page.start_work(lot_number, start_time_str)
        self.home_page.set_status(f"착공 완료: {lot_number}", "success")



        # Start elapsed timer
        self.elapsed_timer.start(1000)

        # Show toast
        Toast.success(self, f"착공 완료: {lot_number}")



    @safe_slot("완공 처리 실패", show_dialog=True)
    def _on_work_completed(self, message: str):
        """Handle work completed event."""
        complete_time = datetime.now().strftime("%H:%M:%S")

        # Stop elapsed timer
        self.elapsed_timer.stop()

        # Update home page
        self.home_page.complete_work(complete_time)
        self.home_page.set_status(message, "success")



        # Reset state
        self.current_lot = None
        self.start_time = None

        # Show toast
        Toast.success(self, message)

    def _on_error(self, error_msg: str):
        """Handle error event."""
        logger.error(error_msg)

        # Re-enable controls based on current state
        if self.current_lot:
            self.home_page.set_enabled(True)  # This might need refinement depending on exactly what we want to enable
        else:
            self.home_page.set_enabled(True)

        # Update home page
        self.home_page.set_status(f"오류: {error_msg}", "danger")

        # Show toast
        Toast.danger(self, f"오류: {error_msg}")

    def _on_connection_status_changed(self, is_online: bool):
        """Handle connection status change."""
        if is_online:
            self.connection_indicator.set_status("success", "온라인")
        else:
            self.connection_indicator.set_status("danger", "오프라인")

    def _update_elapsed_time(self):
        """Update elapsed time display."""
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            elapsed_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            # Update home page
            self.home_page.work_card.update_time(elapsed_str)

    def eventFilter(self, obj, event):
        """
        Global event filter for barcode scanner input.

        Captures keyboard events and forwards to barcode service.
        """
        if event.type() == QEvent.KeyPress:
            key_event = event
            key = key_event.text()

            # Only process printable characters and Enter
            if key or key_event.key() in (Qt.Key_Return, Qt.Key_Enter):
                if key_event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    self.barcode_service.process_key('\n')
                else:
                    self.barcode_service.process_key(key)

        return super().eventFilter(obj, event)

    @safe_slot("LOT 바코드 처리 실패")
    def _on_lot_barcode_scanned(self, lot_number: str):
        """
        Handle LOT barcode scanned.

        Routes to appropriate page based on current context.
        """
        logger.info(f"LOT barcode scanned: {lot_number}")

        current_index = self.stack.currentIndex()
        current_page_data = self.nav_list.item(current_index).data(Qt.UserRole) if current_index < self.nav_list.count() else None

        # Route to appropriate handler based on current page
        if current_page_data == "home":
            # Auto-fill LOT input on home page
            self.home_page.set_lot_number(lot_number)
            Toast.success(self, f"LOT 스캔: {lot_number}")



        else:
            # Generic notification
            Toast.info(self, f"LOT 스캔: {lot_number}")

    @safe_slot("Serial 바코드 처리 실패")
    def _on_serial_barcode_scanned(self, serial_number: str):
        """
        Handle Serial barcode scanned.

        Routes to appropriate page based on current context.
        """
        logger.info(f"Serial barcode scanned: {serial_number}")

        current_index = self.stack.currentIndex()
        current_page_data = self.nav_list.item(current_index).data(Qt.UserRole) if current_index < self.nav_list.count() else None

        # Route to appropriate handler based on current page
        if current_page_data == "home":
            # Auto-fill Serial input on home page - REMOVED as requested
            # self.home_page.set_serial_number(serial_number)
            Toast.success(self, f"Serial 스캔: {serial_number}")

        else:
            # Generic notification
            Toast.info(self, f"Serial 스캔: {serial_number}")

    @safe_slot("잘못된 바코드 처리 실패")
    def _on_invalid_barcode(self, barcode: str):
        """Handle invalid barcode scanned."""
        logger.warning(f"Invalid barcode scanned: {barcode}")
        Toast.warning(self, f"잘못된 바코드 형식: {barcode}")
