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
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction

from views.pages.home_page import HomePage
from views.pages.start_work_page import StartWorkPage
from views.pages.complete_work_page import CompleteWorkPage
from views.pages.settings_page import SettingsPage
from views.pages.help_page import HelpPage
from views.defect_dialog import DefectDialog
from widgets.base_components import StatusIndicator
from widgets.toast_notification import Toast
from utils.theme_manager import get_theme
from utils.process_data_generator import ProcessDataGenerator

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
        self.setMinimumSize(800, 600)
        self.resize(900, 700)

        # Work state tracking
        self.current_lot = None
        self.start_time = None

        # Timer for elapsed time updates
        self.elapsed_timer = QTimer()
        self.elapsed_timer.timeout.connect(self._update_elapsed_time)

        self.setup_ui()
        self.setup_menu()
        self.connect_signals()

        logger.info("MainWindow initialized with sidebar navigation")

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
            ("착공", "start"),
            ("완공", "complete"),
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
        self.start_page = StartWorkPage(self.config)
        self.complete_page = CompleteWorkPage(self.config)
        # Get print_service for settings page
        print_service = getattr(self.viewmodel, 'print_service', None)
        self.settings_page = SettingsPage(self.config, print_service)
        self.help_page = HelpPage(self.config)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.start_page)
        self.stack.addWidget(self.complete_page)
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.help_page)

        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("status_bar")
        self.setStatusBar(self.status_bar)

        # Connection indicator
        self.connection_indicator = StatusIndicator("온라인", status="success")
        self.connection_indicator.setObjectName("connection_indicator")
        self.status_bar.addPermanentWidget(self.connection_indicator)

        # Process info in status bar
        process_label = QLabel(f"공정: {self.config.process_name}")
        process_label.setStyleSheet("color: #9ca3af; font-size: 11px;")
        self.status_bar.addWidget(process_label)

        # Select first item (Home)
        self.nav_list.setCurrentRow(0)

        # Apply styles
        self._apply_styles()

        # Connect page signals
        self._connect_page_signals()

    def _apply_styles(self):
        """Apply styles for sidebar navigation."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
            }

            #main_sidebar {
                background-color: #0a0a0a;
                border-right: 1px solid #1a1a1a;
            }

            #main_nav {
                background-color: transparent;
                border: none;
                outline: none;
            }

            #main_nav::item {
                padding: 14px 16px;
                border-left: 3px solid transparent;
                color: #9ca3af;
                font-size: 13px;
            }

            #main_nav::item:selected {
                background-color: #1a1a1a;
                border-left: 3px solid #3ECF8E;
                color: #3ECF8E;
                font-weight: 600;
            }

            #main_nav::item:hover:!selected {
                background-color: #0f0f0f;
            }

            #main_content {
                background-color: #0a0a0a;
            }

            QStatusBar {
                background-color: #0a0a0a;
                border-top: 1px solid #1a1a1a;
                color: #6b7280;
                font-size: 11px;
            }
        """)

    def _connect_page_signals(self):
        """Connect page signals to handlers."""
        # Start page signals
        self.start_page.start_requested.connect(self._on_start_work_requested)

        # Complete page signals
        self.complete_page.pass_requested.connect(self._on_pass_requested)
        self.complete_page.fail_requested.connect(self._on_fail_requested)

    def setup_menu(self):
        """Setup menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("파일(&F)")

        exit_action = QAction("종료(&X)", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("도움말(&H)")

        about_action = QAction("정보(&A)", self)
        about_action.triggered.connect(self._on_about_clicked)
        help_menu.addAction(about_action)

    def connect_signals(self):
        """Connect ViewModel signals to UI updates."""
        self.viewmodel.lot_updated.connect(self._on_lot_updated)
        self.viewmodel.work_started.connect(self._on_work_started)
        self.viewmodel.work_completed.connect(self._on_work_completed)
        self.viewmodel.error_occurred.connect(self._on_error)
        self.viewmodel.connection_status_changed.connect(
            self._on_connection_status_changed
        )

    def _on_nav_changed(self, index):
        """Handle navigation item change."""
        item = self.nav_list.item(index)
        if not item:
            return

        page_type = item.data(Qt.UserRole)
        self.stack.setCurrentIndex(index)

        # Focus on input when switching to start page
        if page_type == "start":
            self.start_page.focus_input()

    def _on_start_work_requested(self, lot_number: str):
        """Handle start work request from start page."""
        if not lot_number:
            Toast.warning(self, "LOT 번호를 입력하세요.")
            return

        # Disable start controls during request
        self.start_page.set_enabled(False)

        # Call viewmodel to start work
        self.viewmodel.start_work(lot_number)

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
        self.complete_page.set_enabled(False)

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
            self.complete_page.set_enabled(False)

            # Call viewmodel to complete work
            self.viewmodel.complete_work(completion_data)

    def _on_lot_updated(self, lot_data: dict):
        """Handle LOT information update."""
        if lot_data:
            self.current_lot = lot_data.get("lot_number")
        else:
            self.current_lot = None
            self.start_time = None

    def _on_work_started(self, lot_number: str):
        """Handle work started event."""
        self.current_lot = lot_number
        self.start_time = datetime.now()
        start_time_str = self.start_time.strftime("%H:%M:%S")

        # Update home page
        self.home_page.start_work(lot_number, start_time_str)
        self.home_page.set_status(f"착공 완료: {lot_number}", "success")

        # Update complete page
        self.complete_page.set_work_info(lot_number, "00:00:00")
        self.complete_page.set_enabled(True)

        # Update start page
        self.start_page.clear_input()
        self.start_page.set_enabled(False)

        # Start elapsed timer
        self.elapsed_timer.start(1000)

        # Show toast
        Toast.success(self, f"착공 완료: {lot_number}")

        # Switch to home page to show status
        self.nav_list.setCurrentRow(0)

    def _on_work_completed(self, message: str):
        """Handle work completed event."""
        complete_time = datetime.now().strftime("%H:%M:%S")

        # Stop elapsed timer
        self.elapsed_timer.stop()

        # Update home page
        self.home_page.complete_work(complete_time)
        self.home_page.set_status(message, "success")
        self.home_page.set_recent_message(message)

        # Reset complete page
        self.complete_page.reset()

        # Enable start page for next work
        self.start_page.set_enabled(True)

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
            self.complete_page.set_enabled(True)
        else:
            self.start_page.set_enabled(True)

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

            # Update complete page
            self.complete_page.update_elapsed_time(elapsed_str)

    def _on_about_clicked(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "F2X NeuroHub Production Tracker",
            f"<h3>F2X NeuroHub 공정 추적 앱</h3>"
            f"<p>공정: {self.config.process_name}</p>"
            f"<p>Version: 1.0.0</p>"
            f"<p>© 2025 F2X. All rights reserved.</p>"
        )

    def closeEvent(self, event):
        """Handle window close event with proper cleanup."""
        reply = QMessageBox.question(
            self,
            "종료 확인",
            "앱을 종료하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            logger.info("Application closing - initiating cleanup")

            # Stop timers
            self.elapsed_timer.stop()

            # Clear all active toasts
            Toast.clear_all()

            # Clean up home page
            self.home_page.cleanup()

            # Clean up ViewModel resources
            self.viewmodel.cleanup()

            logger.info("Application cleanup completed")
            event.accept()
        else:
            event.ignore()
