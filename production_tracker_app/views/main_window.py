"""
Main Window for Production Tracker App.
"""
import logging

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QStatusBar, QMessageBox, QPushButton, QFrame
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QAction
from widgets.process_info_card import ProcessInfoCard
from widgets.work_status_card import WorkStatusCard
from widgets.base_components import StatusIndicator, ThemedLabel
from widgets.toast_notification import Toast
from utils.theme_manager import get_theme

logger = logging.getLogger(__name__)
theme = get_theme()


class MainWindow(QMainWindow):
    """Main application window (400x600px)."""

    def __init__(self, viewmodel, config):
        super().__init__()
        self.viewmodel = viewmodel
        self.config = config

        self.setWindowTitle(f"F2X NeuroHub - {config.process_name}")

        # Get window size from theme
        width = theme.get("layout.windowWidth", 400)
        height = theme.get("layout.windowHeight", 600)
        self.setMinimumSize(width, height)
        self.resize(width, height)

        self.setup_ui()
        self.setup_menu()
        self.connect_signals()

        # Enable barcode input capture
        self.installEventFilter(self)

        logger.info("MainWindow initialized")

    def setup_ui(self):
        """Setup UI components."""
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        # Get margins and spacing from theme
        margin = theme.get("spacing.md", 16)
        spacing = theme.get("spacing.sm", 8)
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.setSpacing(spacing)

        # Process info card
        self.process_card = ProcessInfoCard(self.config)
        layout.addWidget(self.process_card)

        # Work status card
        self.work_card = WorkStatusCard()
        layout.addWidget(self.work_card)

        # Status label (using Property Variant)
        self.status_label = QLabel("바코드 스캔 대기중...")
        self.status_label.setObjectName("status_label")
        self.status_label.setProperty("variant", "body")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Recent completion label (using Property Variant)
        self.recent_label = ThemedLabel("", variant="caption")
        self.recent_label.setObjectName("recent_label")
        self.recent_label.setAlignment(Qt.AlignCenter)
        self.recent_label.setWordWrap(True)
        layout.addWidget(self.recent_label)

        # Label printing section (Process 7 only)
        self.label_print_section = QFrame()
        self.label_print_section.setObjectName("label_print_section")
        self.label_print_section.setProperty("variant", "card")
        label_print_layout = QVBoxLayout(self.label_print_section)
        label_print_layout.setContentsMargins(12, 12, 12, 12)
        label_print_layout.setSpacing(8)

        # Current serial display
        serial_layout = QHBoxLayout()
        serial_title = ThemedLabel("현재 시리얼:", variant="body")
        self.serial_display = ThemedLabel("-", variant="heading")
        self.serial_display.setObjectName("serial_display")
        serial_layout.addWidget(serial_title)
        serial_layout.addWidget(self.serial_display)
        serial_layout.addStretch()
        label_print_layout.addLayout(serial_layout)

        # Print buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.print_button = QPushButton("라벨 출력")
        self.print_button.setObjectName("print_button")
        self.print_button.setProperty("variant", "primary")
        self.print_button.clicked.connect(self.on_print_clicked)

        self.reprint_button = QPushButton("재출력")
        self.reprint_button.setObjectName("reprint_button")
        self.reprint_button.setProperty("variant", "secondary")
        self.reprint_button.clicked.connect(self.on_reprint_clicked)
        self.reprint_button.setEnabled(False)  # Disabled until first print

        button_layout.addWidget(self.print_button)
        button_layout.addWidget(self.reprint_button)
        label_print_layout.addLayout(button_layout)

        layout.addWidget(self.label_print_section)

        # Show/hide based on process
        if not self.config.is_label_printing_process:
            self.label_print_section.hide()

        layout.addStretch()

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("status_bar")
        self.setStatusBar(self.status_bar)

        # Connection indicator using Property Variant
        self.connection_indicator = StatusIndicator("온라인", status="success")
        self.connection_indicator.setObjectName("connection_indicator")
        self.status_bar.addPermanentWidget(self.connection_indicator)

    def setup_menu(self):
        """Setup menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("파일(&F)")

        exit_action = QAction("종료(&X)", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Settings menu
        settings_menu = menubar.addMenu("설정(&S)")

        config_action = QAction("환경설정(&C)", self)
        config_action.triggered.connect(self.on_settings_clicked)
        settings_menu.addAction(config_action)

        # Help menu
        help_menu = menubar.addMenu("도움말(&H)")

        about_action = QAction("정보(&A)", self)
        about_action.triggered.connect(self.on_about_clicked)
        help_menu.addAction(about_action)

    def connect_signals(self):
        """Connect ViewModel signals to UI updates."""
        self.viewmodel.lot_updated.connect(self.on_lot_updated)
        self.viewmodel.work_started.connect(self.on_work_started)
        self.viewmodel.work_completed.connect(self.on_work_completed)
        self.viewmodel.error_occurred.connect(self.on_error)
        self.viewmodel.connection_status_changed.connect(
            self.on_connection_status_changed
        )

        # Label printing signals (Process 7)
        if hasattr(self.viewmodel, 'serial_received'):
            self.viewmodel.serial_received.connect(self.on_serial_received)
        if hasattr(self.viewmodel, 'label_printed'):
            self.viewmodel.label_printed.connect(self.on_label_printed)

    def eventFilter(self, obj, event):
        """Capture keyboard events for barcode scanner."""
        if event.type() == QEvent.KeyPress:
            key_event = event
            key = key_event.text()
            if key:
                self.viewmodel.barcode_service.process_key(key)
        return super().eventFilter(obj, event)

    def on_lot_updated(self, lot_data: dict):
        """Handle LOT information update."""
        if lot_data:
            worker_id = lot_data.get("worker_id", "-")
            self.process_card.set_worker(worker_id)
            self.work_card.set_lot(lot_data.get("lot_number", "-"))
        else:
            self.process_card.set_worker("-")
            self.work_card.reset()

    def on_work_started(self, lot_number: str):
        """Handle work started event."""
        from datetime import datetime
        start_time = datetime.now().strftime("%H:%M:%S")
        self.work_card.start_work(lot_number, start_time)
        self.status_label.setText(f"착공 완료: {lot_number}")
        # Use Property Variant for styling
        self.status_label.setProperty("variant", "success")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        # Show success toast
        Toast.success(self, f"착공 완료: {lot_number}")

    def on_work_completed(self, message: str):
        """Handle work completed event."""
        from datetime import datetime
        complete_time = datetime.now().strftime("%H:%M:%S")
        self.work_card.complete_work(complete_time)
        self.status_label.setText(message)
        # Use Property Variant for styling
        self.status_label.setProperty("variant", "success")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.recent_label.setText(message)
        # Show success toast
        Toast.success(self, f"완공 완료: {message}")

    def on_error(self, error_msg: str):
        """Handle error event."""
        logger.error(error_msg)
        self.status_label.setText(f"오류: {error_msg}")
        # Use Property Variant for styling
        self.status_label.setProperty("variant", "danger")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        # Show danger toast (replaces QMessageBox for non-blocking UX)
        Toast.danger(self, f"오류: {error_msg}")

    def on_connection_status_changed(self, is_online: bool):
        """Handle connection status change."""
        if is_online:
            self.connection_indicator.set_status("success", "온라인")
        else:
            self.connection_indicator.set_status("danger", "오프라인")

    def on_print_clicked(self):
        """Handle print button click."""
        if not self.viewmodel.current_lot:
            Toast.warning(self, "먼저 LOT 바코드를 스캔하세요.")
            return

        self.print_button.setEnabled(False)
        self.status_label.setText("라벨 출력 중...")
        self.viewmodel.request_serial_and_print()

    def on_reprint_clicked(self):
        """Handle reprint button click."""
        self.reprint_button.setEnabled(False)
        self.status_label.setText("재출력 중...")
        self.viewmodel.reprint_label()

    def on_serial_received(self, serial_number: str):
        """Handle serial number received from server."""
        self.serial_display.setText(serial_number)
        self.reprint_button.setEnabled(True)

    def on_label_printed(self, serial_number: str):
        """Handle successful label print."""
        self.print_button.setEnabled(True)
        self.reprint_button.setEnabled(True)
        self.serial_display.setText(serial_number)
        self.status_label.setText(f"라벨 출력 완료: {serial_number}")
        Toast.success(self, f"라벨 출력 완료: {serial_number}")

    def on_settings_clicked(self):
        """Open settings dialog."""
        from views.settings_dialog import SettingsDialog
        # Pass print_service if available (Process 7)
        print_service = getattr(self.viewmodel, 'print_service', None)
        dialog = SettingsDialog(self.config, print_service, self)
        if dialog.exec():
            Toast.info(self, "설정이 저장되었습니다. 재시작하면 적용됩니다.")

    def on_about_clicked(self):
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
        """Handle window close event with proper thread cleanup."""
        reply = QMessageBox.question(
            self,
            "종료 확인",
            "앱을 종료하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            logger.info("Application closing - initiating cleanup")

            # Clear all active toasts
            Toast.clear_all()

            # Clean up work card timer
            self.work_card.cleanup()

            # Clean up ViewModel resources (stops timers, cancels threads)
            self.viewmodel.cleanup()

            logger.info("Application cleanup completed")
            event.accept()
        else:
            event.ignore()
