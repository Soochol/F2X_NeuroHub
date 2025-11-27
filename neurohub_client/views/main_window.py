"""
Main Window for Production Tracker App with Sidebar Navigation.
"""
import logging
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QStatusBar, QMessageBox, QPushButton, QFrame, QStackedWidget,
    QGraphicsOpacityEffect, QButtonGroup
)
from PySide6.QtCore import Qt, QTimer, QEvent, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QKeyEvent

from views.pages.home_page import HomePage
from views.pages.history_page import HistoryPage
from views.pages.settings_page import SettingsPage
from views.pages.wip_generation_page import WIPGenerationPage
from views.pages.wip_dashboard_page import WIPDashboardPage
from views.defect_dialog import DefectDialog
from views.login_dialog import LoginDialog
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
from services.history_manager import get_history_manager, EventType
from widgets.svg_icon import SvgIcon

logger = logging.getLogger(__name__)
theme = get_theme()


class NavItemWidget(QPushButton):
    """Navigation item widget with SVG icon and label."""

    def __init__(self, icon_name: str, label: str, parent=None):
        super().__init__(parent)
        self._icon_name = icon_name
        self._label_text = label
        self._is_selected = False

        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(44)

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(12)

        # Icon
        self._icon = SvgIcon(icon_name, theme.get('colors.grey.400'), 20)
        layout.addWidget(self._icon)

        # Label
        self._label = QLabel(label)
        self._label.setObjectName("nav_label")
        layout.addWidget(self._label)
        layout.addStretch()

        self._apply_style()

    def _apply_style(self):
        """Apply button styling."""
        bg_default = theme.get('colors.background.default')
        bg_elevated = theme.get('colors.background.elevated')
        border = theme.get('colors.border.default')
        grey_400 = theme.get('colors.grey.400')
        brand = theme.get('colors.brand.main')

        self.setStyleSheet(f"""
            NavItemWidget {{
                background-color: transparent;
                border: none;
                border-left: 3px solid transparent;
                text-align: left;
            }}
            NavItemWidget:hover {{
                background-color: {bg_default};
            }}
            NavItemWidget:checked {{
                background-color: {border};
                border-left: 3px solid {brand};
            }}
            #nav_label {{
                color: {grey_400};
                font-size: 13px;
                background: transparent;
            }}
        """)

    def set_selected(self, selected: bool):
        """Set selection state."""
        self._is_selected = selected
        self.setChecked(selected)

        brand = theme.get('colors.brand.main')
        grey_400 = theme.get('colors.grey.400')

        if selected:
            self._icon.set_color(brand)
            self._label.setStyleSheet(f"color: {brand}; font-weight: 600; background: transparent;")
        else:
            self._icon.set_color(grey_400)
            self._label.setStyleSheet(f"color: {grey_400}; font-weight: normal; background: transparent;")

    def set_expanded(self, expanded: bool):
        """Show/hide label based on sidebar state."""
        self._label.setVisible(expanded)

    def get_icon_name(self) -> str:
        return self._icon_name


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation."""

    def __init__(self, viewmodel, config):
        super().__init__()
        self.viewmodel = viewmodel
        self.config = config

        self.setWindowTitle(f"F2X NeuroHub - {config.process_name}")

        # Window size for sidebar layout
        self.setMinimumSize(900, 771)
        self.resize(900, 771)

        # Work state tracking
        self.current_lot = None
        self.start_time = None

        # Sidebar state
        self._sidebar_expanded = True
        self._sidebar_width_expanded = 160
        self._sidebar_width_collapsed = 50

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

    def showEvent(self, event):
        """Refresh home page when window is first shown (after login)."""
        super().showEvent(event)
        # Validate and refresh user info after login
        auth_service = getattr(self.viewmodel, 'auth_service', None)
        if auth_service and auth_service.access_token:
            # Validate current token by fetching user info from /me endpoint
            logger.info("Validating user info after login...")
            auth_service.validate_token()
            # Small delay to ensure validation completes before refresh
            from PySide6.QtCore import QTimer
            if hasattr(self, 'home_page'):
                QTimer.singleShot(500, self.home_page.refresh_info)
                logger.info("Home page info refresh scheduled")
        elif hasattr(self, 'home_page'):
            # No token, just refresh immediately
            self.home_page.refresh_info()
            logger.info("Home page info refreshed on window show")

    def setup_ui(self):
        """Setup UI components with sidebar navigation."""
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setObjectName("main_sidebar")
        self.sidebar.setFixedWidth(self._sidebar_width_expanded)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Hamburger button container
        hamburger_container = QWidget()
        hamburger_container.setObjectName("hamburger_container")
        hamburger_layout = QHBoxLayout(hamburger_container)
        hamburger_layout.setContentsMargins(8, 8, 8, 8)
        hamburger_layout.setSpacing(8)

        # Hamburger button
        self.hamburger_btn = QPushButton()
        self.hamburger_btn.setObjectName("hamburger_btn")
        self.hamburger_btn.setCursor(Qt.PointingHandCursor)
        self.hamburger_btn.setFixedSize(34, 34)
        self.hamburger_btn.clicked.connect(self._toggle_sidebar)

        # SVG icon for hamburger
        self._hamburger_icon = SvgIcon(
            "hamburger",
            theme.get('colors.grey.400'),
            20
        )
        hamburger_btn_layout = QHBoxLayout(self.hamburger_btn)
        hamburger_btn_layout.setContentsMargins(0, 0, 0, 0)
        hamburger_btn_layout.addWidget(
            self._hamburger_icon, alignment=Qt.AlignCenter
        )

        hamburger_layout.addWidget(self.hamburger_btn)

        # App name label
        self.app_name_label = QLabel("F2X NeuroHub")
        self.app_name_label.setObjectName("app_name_label")
        self.app_name_label.setFixedHeight(34)  # Match hamburger button height
        self.app_name_label.setStyleSheet(f"""
            QLabel#app_name_label {{
                color: {theme.get('colors.text.primary')};
                font-size: 14px;
                font-weight: 700;
                background: transparent;
                padding-top: 11px;
            }}
        """)
        hamburger_layout.addWidget(self.app_name_label)

        hamburger_layout.addStretch()
        sidebar_layout.addWidget(hamburger_container)

        # Navigation container
        nav_container = QWidget()
        nav_container.setObjectName("nav_container")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(2)

        # Navigation items with icons
        self._nav_items_data = [
            ("홈", "home", "home"),
            ("작업 이력", "history", "history"),
            ("설정", "settings", "settings"),
        ]

        # Create nav item widgets
        self._nav_buttons = []
        self._nav_button_group = QButtonGroup(self)
        self._nav_button_group.setExclusive(True)

        for idx, (label, data, icon_name) in enumerate(self._nav_items_data):
            nav_item = NavItemWidget(icon_name, label)
            nav_item.setProperty("page_data", data)
            nav_item.setProperty("page_index", idx)
            nav_item.clicked.connect(lambda checked, i=idx: self._on_nav_clicked(i))
            self._nav_buttons.append(nav_item)
            self._nav_button_group.addButton(nav_item, idx)
            nav_layout.addWidget(nav_item)

        nav_layout.addStretch()
        sidebar_layout.addWidget(nav_container)
        sidebar_layout.addStretch()

        # User info and logout at bottom of sidebar
        bottom_container = QWidget()
        bottom_container.setObjectName("bottom_container")
        bottom_layout = QVBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 8, 0, 8)
        bottom_layout.setSpacing(8)

        # User info section
        self.user_info_widget = QWidget()
        self.user_info_widget.setObjectName("user_info_widget")
        user_info_layout = QHBoxLayout(self.user_info_widget)
        user_info_layout.setContentsMargins(10, 0, 0, 0)
        user_info_layout.setSpacing(8)

        # User name labels container
        user_labels_widget = QWidget()
        user_labels_layout = QVBoxLayout(user_labels_widget)
        user_labels_layout.setContentsMargins(0, 0, 0, 0)
        user_labels_layout.setSpacing(0)

        self.user_name_label = QLabel("")
        self.user_name_label.setObjectName("user_name_label")
        self.user_name_label.setStyleSheet(f"""
            QLabel#user_name_label {{
                color: {theme.get('colors.text.primary')};
                font-size: 12px;
                font-weight: 600;
            }}
        """)
        user_labels_layout.addWidget(self.user_name_label)

        self.user_id_label = QLabel("")
        self.user_id_label.setObjectName("user_id_label")
        self.user_id_label.setStyleSheet(f"""
            QLabel#user_id_label {{
                color: {theme.get('colors.grey.500')};
                font-size: 10px;
            }}
        """)
        user_labels_layout.addWidget(self.user_id_label)

        user_info_layout.addWidget(user_labels_widget)
        user_info_layout.addStretch()

        bottom_layout.addWidget(self.user_info_widget)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {theme.get('colors.border.default')}; max-height: 1px;")
        bottom_layout.addWidget(separator)

        # Logout button
        self.logout_btn = NavItemWidget("logout", "로그아웃")
        self.logout_btn.setCheckable(False)  # Not a navigation item
        self.logout_btn.clicked.connect(self._on_logout_clicked)

        # Apply danger color styling for logout (same pattern as home button but with danger color)
        danger = theme.get('colors.danger.main')
        bg_default = theme.get('colors.background.default')
        self.logout_btn.setStyleSheet(f"""
            NavItemWidget {{
                background-color: transparent;
                border: none;
                border-left: 3px solid transparent;
                text-align: left;
            }}
            NavItemWidget:hover {{
                background-color: {bg_default};
                border-left: 3px solid {danger};
            }}
        """)
        # Set icon and label color directly (same as NavItemWidget.set_selected but with danger color)
        self.logout_btn._icon.set_color(danger)
        self.logout_btn._label.setStyleSheet(f"color: {danger}; font-size: 13px; font-weight: normal; background: transparent;")

        bottom_layout.addWidget(self.logout_btn)
        sidebar_layout.addWidget(bottom_container)

        # Initialize user info display
        self._update_user_info_display()

        main_layout.addWidget(self.sidebar)

        # Content area
        content_widget = QWidget()
        content_widget.setObjectName("main_content")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(16)

        # Stacked widget for pages
        self.stack = QStackedWidget()

        # Get services from viewmodel
        auth_service = getattr(self.viewmodel, 'auth_service', None)
        api_client = getattr(self.viewmodel, 'api_client', None)

        # Create pages
        self.home_page = HomePage(self.config, auth_service)

        # History manager for tracking events
        self.history_manager = get_history_manager()

        # Create history page
        self.history_page = HistoryPage(self.config)

        # Create settings page
        self.settings_page = SettingsPage(self.config, api_client)

        # Add pages to stack (order must match nav_items)
        self.stack.addWidget(self.home_page)      # index 0: home
        self.stack.addWidget(self.history_page)   # index 1: history
        self.stack.addWidget(self.settings_page)  # index 2: settings

        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("status_bar")
        self.setStatusBar(self.status_bar)

        # TCP Client status indicator (equipment connection)
        self.tcp_client_indicator = StatusIndicator("장비: 대기 중", "body")
        self.status_bar.addPermanentWidget(self.tcp_client_indicator)

        # Backend connection status indicator
        self.connection_indicator = StatusIndicator("백엔드: 연결 중", "body")
        self.status_bar.addPermanentWidget(self.connection_indicator)

        # Select first item (Home)
        self._select_nav_item(0)

        # Apply styles
        self._apply_styles()

        # Connect page signals
        self._connect_page_signals()

    def _apply_styles(self):
        """Apply styles for sidebar navigation."""
        bg_dark = theme.get('colors.background.dark')
        bg_default = theme.get('colors.background.default')
        bg_elevated = theme.get('colors.background.elevated')
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

            #hamburger_container {{
                background-color: transparent;
            }}

            #hamburger_btn {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
            }}

            #hamburger_btn:hover {{
                background-color: {bg_elevated};
            }}

            #nav_container {{
                background-color: transparent;
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
            self.home_page.measurement_confirmed,
            self._on_measurement_confirmed,
            "measurement_confirmed -> _on_measurement_confirmed"
        ).connect(
            self.home_page.measurement_cancelled,
            self._on_measurement_cancelled,
            "measurement_cancelled -> _on_measurement_cancelled"
        ).connect(
            self.settings_page.settings_saved,
            self._on_settings_saved,
            "settings_saved -> _on_settings_saved"
        ).connect(
            self.settings_page.data_refreshed,
            self._on_settings_data_refreshed,
            "data_refreshed -> _on_settings_data_refreshed"
        )

        if not connector.all_connected():
            logger.error(
                f"페이지 시그널 연결 실패: {connector.failed_connections}"
            )

    @safe_slot("설정 저장 후 처리 실패")
    def _on_settings_saved(self):
        """Handle settings saved - refresh page info."""
        self.home_page.refresh_info()

    @safe_slot("설정 데이터 새로고침 처리 실패")
    def _on_settings_data_refreshed(self, data_type: str, count: int):
        """Handle settings data refreshed from API."""
        Toast.success(self, f"{data_type} 목록 새로고침 완료 ({count}건)")

    @safe_slot("로그아웃 클릭 처리 실패")
    def _on_logout_clicked(self):
        """Handle logout button click from sidebar."""
        reply = QMessageBox.question(
            self,
            "로그아웃",
            "로그아웃 하시겠습니까?\n\n다시 로그인해야 앱을 사용할 수 있습니다.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self._perform_logout()

    def _perform_logout(self):
        """Perform the actual logout and show re-login dialog."""
        logger.info("Processing logout request...")

        # Get auth service
        auth_service = getattr(self.viewmodel, 'auth_service', None)
        if not auth_service:
            logger.error("Auth service not available")
            Toast.danger(self, "로그아웃 실패: 인증 서비스를 찾을 수 없습니다.")
            return

        # Stop any active work before logout
        if self.current_lot:
            Toast.warning(self, "진행 중인 작업이 있습니다. 먼저 작업을 완료해주세요.")
            return

        # Perform logout
        auth_service.logout()
        logger.info("Logout completed, minimizing window and showing login dialog...")

        # Minimize main window
        self.showMinimized()

        # Show login dialog for re-login (parent=None so it appears independently)
        login_dialog = LoginDialog(auth_service, self.config, None)
        result = login_dialog.exec()

        if result:
            # Login successful - restore main window
            logger.info("Re-login successful, restoring window and updating UI...")

            # Restore main window
            self.showNormal()
            self.activateWindow()
            self.raise_()

            # Update user info in sidebar
            self._update_user_info_display()

            # Refresh home page
            self.home_page.refresh_info()

            # Update window title
            self.setWindowTitle(f"F2X NeuroHub - {self.config.process_name}")

            Toast.success(self, "로그인 성공")

            # Navigate to home page
            self._on_nav_clicked(0)
        else:
            # Login cancelled - close the application
            logger.info("Re-login cancelled, closing application...")
            self.close()

    def _toggle_sidebar(self):
        """Toggle sidebar between expanded and collapsed state."""
        self._sidebar_expanded = not self._sidebar_expanded

        if self._sidebar_expanded:
            target_width = self._sidebar_width_expanded
        else:
            target_width = self._sidebar_width_collapsed

        # Show/hide labels in nav items
        for nav_btn in self._nav_buttons:
            nav_btn.set_expanded(self._sidebar_expanded)

        # Also update logout button
        self.logout_btn.set_expanded(self._sidebar_expanded)

        # Show/hide app name label
        self.app_name_label.setVisible(self._sidebar_expanded)

        # Show/hide user info labels
        self.user_name_label.setVisible(self._sidebar_expanded)
        self.user_id_label.setVisible(self._sidebar_expanded)

        # Animate sidebar width
        self._sidebar_animation = QPropertyAnimation(
            self.sidebar, b"minimumWidth"
        )
        self._sidebar_animation.setDuration(200)
        self._sidebar_animation.setStartValue(self.sidebar.width())
        self._sidebar_animation.setEndValue(target_width)
        self._sidebar_animation.setEasingCurve(QEasingCurve.OutCubic)
        self._sidebar_animation.start()

        # Also animate maximum width
        self._sidebar_max_animation = QPropertyAnimation(
            self.sidebar, b"maximumWidth"
        )
        self._sidebar_max_animation.setDuration(200)
        self._sidebar_max_animation.setStartValue(self.sidebar.width())
        self._sidebar_max_animation.setEndValue(target_width)
        self._sidebar_max_animation.setEasingCurve(QEasingCurve.OutCubic)
        self._sidebar_max_animation.start()

    def _update_user_info_display(self):
        """Update user info display in sidebar."""
        auth_service = getattr(self.viewmodel, 'auth_service', None)
        if auth_service and auth_service.current_user:
            user = auth_service.current_user
            full_name = user.get('full_name', '')
            username = user.get('username', '')

            if full_name:
                self.user_name_label.setText(full_name)
                self.user_id_label.setText(f"@{username}")
            else:
                self.user_name_label.setText(username)
                self.user_id_label.setText("")
        else:
            self.user_name_label.setText("로그인 필요")
            self.user_id_label.setText("")

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
        ).connect(
            self.viewmodel.measurement_received,
            self._on_measurement_received,
            "measurement_received -> _on_measurement_received"
        )

        # TCP Server signals
        if self.viewmodel.tcp_server:
            connector.connect(
                self.viewmodel.tcp_server.signals.client_connected,
                self._on_tcp_client_connected,
                "tcp_client_connected -> _on_tcp_client_connected"
            ).connect(
                self.viewmodel.tcp_server.signals.client_disconnected,
                self._on_tcp_client_disconnected,
                "tcp_client_disconnected -> _on_tcp_client_disconnected"
            )

        if not connector.all_connected():
            logger.error(
                f"일부 시그널 연결 실패: {connector.failed_connections}"
            )

    def _select_nav_item(self, index: int):
        """Select a navigation item by index."""
        if 0 <= index < len(self._nav_buttons):
            for i, btn in enumerate(self._nav_buttons):
                btn.set_selected(i == index)
            self._current_nav_index = index

    def _on_nav_clicked(self, index: int):
        """Handle navigation item click."""
        self._select_nav_item(index)

        if 0 <= index < len(self._nav_buttons):
            page_data = self._nav_buttons[index].property("page_data")
            self.stack.setCurrentIndex(index)

            # Focus on input when switching to specific pages
            if page_data == "home":
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
            "wip_id": self.current_lot,
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
                "wip_id": self.current_lot,
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

        # Update home page
        self.home_page.start_work(lot_number, start_time_str)
        self.home_page.set_status(f"착공 완료: {lot_number}", "success")

        # Record to history
        self.history_manager.add_start_event(
            wip_id=lot_number,
            lot_number=lot_number,
            process_name=self.config.process_name,
            success=True,
            message="착공 완료"
        )

        # Start elapsed timer
        self.elapsed_timer.start(1000)

        # Show toast
        Toast.success(self, f"착공 완료: {lot_number}")



    @safe_slot("완공 처리 실패", show_dialog=True)
    def _on_work_completed(self, message: str):
        """Handle work completed event."""
        complete_time_dt = datetime.now()
        complete_time = complete_time_dt.strftime("%H:%M:%S")

        # Calculate duration
        duration = None
        if self.start_time:
            duration = int((complete_time_dt - self.start_time).total_seconds())

        # Stop elapsed timer
        self.elapsed_timer.stop()

        # Update home page
        self.home_page.complete_work(complete_time)
        self.home_page.set_status(message, "success")

        # Determine result from message
        result = "PASS" if "PASS" in message.upper() else "FAIL"

        # Record to history
        self.history_manager.add_complete_event(
            wip_id=self.current_lot or "",
            lot_number=self.current_lot or "",
            result=result,
            process_name=self.config.process_name,
            duration_seconds=duration,
            message=message
        )

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
            self.home_page.set_enabled(True)
        else:
            self.home_page.set_enabled(True)

        # Update home page - show error banner
        self.home_page.show_error(error_msg)

        # Record error to history
        self.history_manager.add_error_event(
            wip_id=self.current_lot or "",
            lot_number=self.current_lot or "",
            error_message=error_msg,
            process_name=self.config.process_name
        )

        # Show toast
        Toast.danger(self, f"오류: {error_msg}")

    def _on_connection_status_changed(self, is_online: bool):
        """Handle connection status change."""
        if is_online:
            self.connection_indicator.set_status("success", "백엔드: 온라인")
        else:
            self.connection_indicator.set_status("danger", "백엔드: 오프라인")

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
        current_page_data = self._nav_buttons[current_index].property("page_data") if current_index < len(self._nav_buttons) else None

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
        current_page_data = self._nav_buttons[current_index].property("page_data") if current_index < len(self._nav_buttons) else None

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

    # --- Measurement Panel Handlers ---

    @safe_slot("측정 데이터 수신 실패")
    def _on_measurement_received(self, equipment_data):
        """
        Handle measurement data received from TCP server.
        Automatically completes work with measurement data.

        Args:
            equipment_data: EquipmentData object from TCP server
        """
        logger.info(f"Measurement received: result={equipment_data.result}")

        if not self.current_lot:
            logger.warning("Measurement received but no active work")
            Toast.warning(self, "진행 중인 작업이 없습니다.")
            return

        # Generate completion time
        complete_time = datetime.now()

        # Get worker_id from auth service
        worker_id = self.viewmodel.auth_service.get_current_user_id()

        # Build completion data with measurements at top level (required by work_service)
        completion_data = {
            "wip_id": self.current_lot,
            "line_id": self.config.line_id,
            "process_id": self.config.process_id,
            "process_name": self.config.process_name,
            "equipment_id": self.config.equipment_id,
            "worker_id": worker_id,
            "start_time": self.start_time.isoformat(),
            "complete_time": complete_time.isoformat(),
            "result": equipment_data.result,
            # measurements must be at top level for work_service.complete_work()
            "measurements": {
                "items": [
                    {
                        "code": m.code,
                        "name": m.name,
                        "value": m.value,
                        "unit": m.unit,
                        "spec": {
                            "min": m.spec.min if m.spec else None,
                            "max": m.spec.max if m.spec else None,
                            "target": m.spec.target if m.spec else None,
                        } if m.spec else None,
                        "result": m.result
                    }
                    for m in equipment_data.measurements
                ]
            },
            # defect_data for failed results
            "defect_data": {
                "defects": [
                    {"code": d.code, "reason": d.reason}
                    for d in equipment_data.defects
                ]
            } if equipment_data.defects else None
        }

        # Disable buttons during request
        self.home_page.set_enabled(False)

        # Clear pending measurement (not needed anymore but keep for safety)
        self.viewmodel.clear_pending_measurement()

        # Call viewmodel to complete work
        logger.info(f"Auto-completing work: WIP={self.current_lot}, result={equipment_data.result}")
        self.viewmodel.complete_work(completion_data)
        Toast.info(self, f"완공 처리 중: {equipment_data.result}")

    @safe_slot("측정 확인 처리 실패")
    def _on_measurement_confirmed(self):
        """Handle measurement confirmation - complete work with measurement data."""
        if not self.current_lot:
            Toast.warning(self, "진행 중인 작업이 없습니다.")
            return

        pending = self.viewmodel.pending_measurement
        if not pending:
            Toast.warning(self, "측정 데이터가 없습니다.")
            return

        # Generate completion time
        complete_time = datetime.now()

        # Build process data from measurement
        process_data = {
            "measurements": [
                {
                    "code": m.code,
                    "name": m.name,
                    "value": m.value,
                    "unit": m.unit,
                    "spec": {
                        "min": m.spec.min if m.spec else None,
                        "max": m.spec.max if m.spec else None,
                        "target": m.spec.target if m.spec else None,
                    } if m.spec else None,
                    "result": m.result
                }
                for m in pending.measurements
            ],
            "defects": [
                {"code": d.code, "reason": d.reason}
                for d in pending.defects
            ]
        }

        # Get worker_id from auth service
        worker_id = self.viewmodel.auth_service.get_current_user_id()

        # Build completion data
        completion_data = {
            "wip_id": self.current_lot,
            "line_id": self.config.line_id,
            "process_id": self.config.process_id,
            "process_name": self.config.process_name,
            "equipment_id": self.config.equipment_id,
            "worker_id": worker_id,
            "start_time": self.start_time.isoformat(),
            "complete_time": complete_time.isoformat(),
            "result": pending.result,
            "process_data": process_data
        }

        # Disable buttons during request
        self.home_page.set_enabled(False)

        # Clear pending measurement
        self.viewmodel.clear_pending_measurement()

        # Call viewmodel to complete work
        self.viewmodel.complete_work(completion_data)

    @safe_slot("측정 취소 처리 실패")
    def _on_measurement_cancelled(self):
        """Handle measurement cancellation - discard measurement data."""
        logger.info("Measurement cancelled by user")

        # Clear pending measurement
        self.viewmodel.clear_pending_measurement()

        # Re-enable PASS/FAIL buttons if work is in progress and user has permission
        if self.current_lot and self.home_page._can_complete_work():
            self.home_page.pass_button.setEnabled(True)
            self.home_page.fail_button.setEnabled(True)

        Toast.info(self, "측정이 취소되었습니다.")

    # --- TCP Server Client Status Handlers ---

    @safe_slot("TCP 클라이언트 연결 처리 실패")
    def _on_tcp_client_connected(self, client_addr: str):
        """Handle TCP client connected."""
        logger.info(f"TCP client connected: {client_addr}")
        msg = f"장비: 연결됨 ({client_addr})"
        self.tcp_client_indicator.set_status("success", msg)

    @safe_slot("TCP 클라이언트 해제 처리 실패")
    def _on_tcp_client_disconnected(self, client_addr: str):
        """Handle TCP client disconnected."""
        logger.info(f"TCP client disconnected: {client_addr}")
        self.tcp_client_indicator.set_status("body", "장비: 대기 중")
