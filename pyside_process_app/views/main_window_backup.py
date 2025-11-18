"""Main Window - Primary application window"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QStatusBar, QMenuBar, QMenu, QMessageBox, QPushButton
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QFont
from viewmodels.main_viewmodel import MainViewModel
from config import AppConfig


class MainWindow(QMainWindow):
    """Primary application window"""

    def __init__(self, viewmodel: MainViewModel, config: AppConfig, app_state, history_service, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.config = config
        self.app_state = app_state
        self.history_service = history_service
        self.setWindowTitle("F2X NeuroHub MES - 공정 관리 시스템")
        self.setMinimumSize(1024, 768)

        self.setup_ui()
        self.connect_signals()

        # Load saved geometry if exists
        if self.config.window_geometry:
            self.restoreGeometry(self.config.window_geometry)

    def setup_ui(self):
        """Setup UI layout"""
        # Create menu bar
        self.create_menu_bar()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()

        # Header section
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)

        # Stats section
        stats_layout = self.create_stats_section()
        main_layout.addLayout(stats_layout)

        # Content area placeholder
        content_label = QLabel("공정 관리 화면 (개발 중)")
        content_label.setAlignment(Qt.AlignCenter)
        content_label.setStyleSheet("font-size: 18px; color: #666;")
        main_layout.addWidget(content_label, 1)

        central_widget.setLayout(main_layout)

        # Status bar with connection indicator
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Connection status label
        self.connection_status_label = QLabel("🟢 온라인")
        self.connection_status_label.setStyleSheet("padding: 0 10px; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.connection_status_label)

        # Offline queue label
        self.offline_queue_label = QLabel("큐: 0")
        self.offline_queue_label.setStyleSheet("padding: 0 10px;")
        self.offline_queue_label.setVisible(False)  # Hidden when queue is empty
        self.status_bar.addPermanentWidget(self.offline_queue_label)

        # Manual retry button
        self.retry_button = QPushButton("재시도")
        self.retry_button.setStyleSheet("padding: 2px 10px;")
        self.retry_button.clicked.connect(self.on_manual_retry)
        self.retry_button.setVisible(False)  # Hidden when online
        self.status_bar.addPermanentWidget(self.retry_button)

        self.status_bar.showMessage("준비")

    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("파일(&F)")

        exit_action = QAction("종료(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("보기(&V)")

        refresh_action = QAction("새로고침(&R)", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.on_refresh)
        view_menu.addAction(refresh_action)

        view_menu.addSeparator()

        history_action = QAction("작업 이력(&H)", self)
        history_action.setShortcut("Ctrl+H")
        history_action.triggered.connect(self.on_show_history)
        view_menu.addAction(history_action)

        # Settings menu
        settings_menu = menubar.addMenu("설정(&S)")

        config_action = QAction("환경설정(&C)", self)
        config_action.triggered.connect(self.on_settings)
        settings_menu.addAction(config_action)

        # Help menu
        help_menu = menubar.addMenu("도움말(&H)")

        about_action = QAction("정보(&A)", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

    def create_header(self) -> QHBoxLayout:
        """Create header section"""
        layout = QHBoxLayout()

        # Process info
        process_label = QLabel(f"공정: {self.config.process_name} (P{self.config.process_number})")
        process_font = QFont()
        process_font.setPointSize(14)
        process_font.setBold(True)
        process_label.setFont(process_font)

        # User info
        user_name = "Unknown"
        if self.app_state.current_user:
            user_name = self.app_state.current_user.get('username', 'Unknown')
        user_label = QLabel(f"작업자: {user_name}")

        layout.addWidget(process_label)
        layout.addStretch()
        layout.addWidget(user_label)

        return layout

    def create_stats_section(self) -> QHBoxLayout:
        """Create statistics section"""
        layout = QHBoxLayout()

        # Stats labels
        self.stats_labels = {}
        stats_items = [
            ('today_started', '금일 착공'),
            ('today_completed', '금일 완공'),
            ('today_passed', '합격'),
            ('today_failed', '불합격'),
            ('in_progress', '진행중')
        ]

        for key, label_text in stats_items:
            stat_widget = QWidget()
            stat_layout = QVBoxLayout()

            label = QLabel(label_text)
            label.setAlignment(Qt.AlignCenter)

            value_label = QLabel("0")
            value_label.setAlignment(Qt.AlignCenter)
            value_font = QFont()
            value_font.setPointSize(20)
            value_font.setBold(True)
            value_label.setFont(value_font)

            stat_layout.addWidget(label)
            stat_layout.addWidget(value_label)
            stat_widget.setLayout(stat_layout)

            self.stats_labels[key] = value_label
            layout.addWidget(stat_widget)

        return layout

    def connect_signals(self):
        """Connect ViewModel signals to UI slots"""
        self.viewmodel.stats_updated.connect(self.on_stats_updated)
        self.viewmodel.error_occurred.connect(self.on_error)
        self.viewmodel.status_message.connect(self.on_status_message)
        self.viewmodel.connection_status_changed.connect(self.on_connection_status_changed)
        self.viewmodel.offline_queue_changed.connect(self.on_offline_queue_changed)

    @Slot(dict)
    def on_stats_updated(self, stats: dict):
        """Update statistics display"""
        for key, value_label in self.stats_labels.items():
            value = stats.get(key, 0)
            value_label.setText(str(value))

    @Slot(str)
    def on_error(self, message: str):
        """Show error message"""
        QMessageBox.critical(self, "오류", message)
        self.status_bar.showMessage(f"오류: {message}", 5000)

    @Slot(str)
    def on_status_message(self, message: str):
        """Update status bar"""
        self.status_bar.showMessage(message, 3000)

    def on_refresh(self):
        """Refresh data"""
        self.viewmodel.load_daily_stats()
        self.status_bar.showMessage("새로고침 완료", 2000)

    def on_show_history(self):
        """Show history dialog"""
        from views.history_dialog import HistoryDialog
        history_dialog = HistoryDialog(self.history_service, self.config, self.app_state, self)
        history_dialog.exec()

    def on_settings(self):
        """Show settings dialog"""
        QMessageBox.information(self, "환경설정", "환경설정 기능은 개발 중입니다.")

    def on_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "F2X NeuroHub MES 정보",
            "F2X NeuroHub MES\n"
            "공정 관리 시스템\n\n"
            f"현재 공정: {self.viewmodel.process_name}\n"
            f"Version: 1.0.0"
        )

    @Slot(bool)
    def on_connection_status_changed(self, is_online: bool):
        """Update connection status display"""
        if is_online:
            self.connection_status_label.setText("🟢 온라인")
            self.connection_status_label.setStyleSheet("padding: 0 10px; font-weight: bold; color: green;")
            self.retry_button.setVisible(False)
            self.status_bar.showMessage("연결이 복구되었습니다", 3000)
        else:
            self.connection_status_label.setText("🔴 오프라인")
            self.connection_status_label.setStyleSheet("padding: 0 10px; font-weight: bold; color: red;")
            self.retry_button.setVisible(True)
            self.status_bar.showMessage("오프라인 모드 - 데이터가 로컬에 저장됩니다", 5000)

    @Slot(int)
    def on_offline_queue_changed(self, queue_size: int):
        """Update offline queue display"""
        if queue_size > 0:
            self.offline_queue_label.setText(f"큐: {queue_size}")
            self.offline_queue_label.setVisible(True)
        else:
            self.offline_queue_label.setVisible(False)

    def on_manual_retry(self):
        """Manual retry of offline queue"""
        self.viewmodel.manual_retry_offline_queue()
        self.status_bar.showMessage("오프라인 큐를 처리 중입니다...", 3000)

    def closeEvent(self, event):
        """Handle window close event"""
        # Save window geometry
        self.config.window_geometry = self.saveGeometry()
        event.accept()