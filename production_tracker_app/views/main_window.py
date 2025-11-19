"""
Main Window for Production Tracker App.
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel,
                               QStatusBar, QMenuBar, QMenu, QMessageBox)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QAction, QKeyEvent
from widgets.lot_display_card import LotDisplayCard
from widgets.base_components import StatusIndicator, ThemedLabel
from utils.theme_loader import get_current_theme
import logging

logger = logging.getLogger(__name__)
theme = get_current_theme()


class MainWindow(QMainWindow):
    """Main application window (400x600px)."""

    def __init__(self, viewmodel, config):
        super().__init__()
        self.viewmodel = viewmodel
        self.config = config

        self.setWindowTitle(f"F2X NeuroHub - {config.process_name}")

        # Get window size from theme
        if theme:
            width = theme.get("layout.windowWidth", 400)
            height = theme.get("layout.windowHeight", 600)
            self.setMinimumSize(width, height)
            self.resize(width, height)
        else:
            self.setMinimumSize(400, 600)
            self.resize(400, 600)

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
        if theme:
            margin = theme.get("spacing.md", 16)
            spacing = theme.get("spacing.sm", 8)
            layout.setContentsMargins(margin, margin, margin, margin)
            layout.setSpacing(spacing)
        else:
            layout.setContentsMargins(16, 16, 16, 16)
            layout.setSpacing(8)

        # Process name label (header)
        self.process_label = QLabel(f"공정: {self.config.process_name}")
        self.process_label.setObjectName("process_label")
        self.process_label.setAlignment(Qt.AlignCenter)
        if theme:
            # Style as title with brand color
            title_size = theme.get("typography.size.title", 18)
            brand_color = theme.get("colors.brand.main", "#3ECF8E")
            self.process_label.setStyleSheet(f"""
                font-size: {title_size}px;
                font-weight: bold;
                color: {brand_color};
                padding: 8px;
            """)
        layout.addWidget(self.process_label)

        # Current LOT card
        self.lot_card = LotDisplayCard()
        self.lot_card.setObjectName("lot_card")
        layout.addWidget(self.lot_card)

        # Status label (using theme)
        self.status_label = QLabel("바코드 스캔 대기중...")
        self.status_label.setObjectName("status_label")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Recent completion label (using themed component)
        self.recent_label = ThemedLabel("", style_type="tertiary")
        self.recent_label.setObjectName("recent_label")
        self.recent_label.setAlignment(Qt.AlignCenter)
        self.recent_label.setWordWrap(True)
        layout.addWidget(self.recent_label)

        layout.addStretch()

        # Status bar (using theme)
        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("status_bar")
        self.setStatusBar(self.status_bar)

        if theme:
            status_bar_style = theme.get_component_style('statusBar', 'default')
            qss = theme.component_to_qss(status_bar_style)
            self.status_bar.setStyleSheet(f"QStatusBar {{ {qss} }}")

        self.connection_indicator = StatusIndicator("온라인", status="online")
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
        self.viewmodel.connection_status_changed.connect(self.on_connection_status_changed)

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
            self.lot_card.update_lot(
                lot_data.get("lot_number", "-"),
                lot_data.get("worker_id", "-"),
                lot_data.get("start_time", "-")
            )
        else:
            self.lot_card.clear()

    def on_work_started(self, lot_number: str):
        """Handle work started event."""
        self.status_label.setText(f"착공 완료: {lot_number}")
        if theme:
            style = theme.get_component_style('statusLabel', 'success')
            qss = theme.component_to_qss(style)
            self.status_label.setStyleSheet(qss)
        else:
            self.status_label.setStyleSheet("font-size: 13px; color: #22c55e;")

    def on_work_completed(self, message: str):
        """Handle work completed event."""
        self.status_label.setText(message)
        if theme:
            style = theme.get_component_style('statusLabel', 'success')
            qss = theme.component_to_qss(style)
            self.status_label.setStyleSheet(qss)
        else:
            self.status_label.setStyleSheet("font-size: 13px; color: #22c55e;")
        self.recent_label.setText(message)

    def on_error(self, error_msg: str):
        """Handle error event."""
        logger.error(error_msg)
        self.status_label.setText(f"오류: {error_msg}")
        if theme:
            style = theme.get_component_style('statusLabel', 'danger')
            qss = theme.component_to_qss(style)
            self.status_label.setStyleSheet(qss)
        else:
            self.status_label.setStyleSheet("font-size: 13px; color: #ef4444;")
        QMessageBox.warning(self, "오류", error_msg)

    def on_connection_status_changed(self, is_online: bool):
        """Handle connection status change."""
        if is_online:
            self.connection_indicator.set_status("online", "온라인")
        else:
            self.connection_indicator.set_status("offline", "오프라인")

    def on_settings_clicked(self):
        """Open settings dialog."""
        from views.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.config, self)
        if dialog.exec():
            QMessageBox.information(self, "설정 저장", "설정이 저장되었습니다.\n변경사항을 적용하려면 앱을 재시작해주세요.")

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

            # Clean up ViewModel resources (stops timers, cancels threads)
            self.viewmodel.cleanup()

            logger.info("Application cleanup completed")
            event.accept()
        else:
            event.ignore()
