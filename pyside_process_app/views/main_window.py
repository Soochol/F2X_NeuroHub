"""Main Window - Primary application window with sidebar layout"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QStatusBar, QMenuBar, QMenu, QMessageBox, QPushButton,
    QFrame, QStackedWidget
)
from PySide6.QtCore import Qt, Slot, QPropertyAnimation, QSize, QEasingCurve, QParallelAnimationGroup
from PySide6.QtGui import QAction, QFont
from viewmodels.main_viewmodel import MainViewModel
from config import AppConfig
from ui_components import StatCard, SidebarButton, LoginButton, get_current_theme, Layout, create_icon


class MainWindow(QMainWindow):
    """Primary application window with sidebar navigation"""

    def __init__(self, viewmodel: MainViewModel, config: AppConfig, app_state, history_service, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.config = config
        self.app_state = app_state
        self.history_service = history_service
        self.setWindowTitle("F2X NeuroHub MES - 공정 관리 시스템")
        self.setMinimumSize(1200, 800)

        # Navigation state
        self.current_page_index = 0
        self.nav_buttons = {}  # page_index -> SidebarButton
        self.stat_cards = {}  # key -> StatCard

        # Sidebar state
        self.sidebar_expanded = True
        self.sidebar = None
        self.hamburger_button = None

        self.setup_ui()
        self.setup_shortcuts()
        self.connect_signals()

        # Load saved geometry if exists
        if self.config.window_geometry:
            self.restoreGeometry(self.config.window_geometry)

    def setup_ui(self):
        """Setup UI layout"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout: [Header (top) | [Sidebar | Content] (bottom)]
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header (top bar)
        header = self.create_header()
        main_layout.addWidget(header)

        # Content layout: [Sidebar | Content]
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self.sidebar = self.create_sidebar()
        content_layout.addWidget(self.sidebar)

        # Content area (stacked widget for multiple pages)
        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self.create_dashboard_view())  # 0: Dashboard
        self.content_stack.addWidget(self.create_process_view())    # 1: Process Work
        self.content_stack.addWidget(self.create_history_view())    # 2: History
        self.content_stack.addWidget(self.create_stats_view())      # 3: Stats
        self.content_stack.addWidget(self.create_settings_view())   # 4: Settings

        content_layout.addWidget(self.content_stack, 1)

        # Add content layout to main layout
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget, 1)

        central_widget.setLayout(main_layout)

        # Status bar with connection indicator
        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("status_bar")
        self.setStatusBar(self.status_bar)

        # Connection status label
        self.connection_status_label = QLabel("🟢 온라인")
        self.connection_status_label.setObjectName("connection_status_label")
        self.connection_status_label.setStyleSheet("padding: 0 10px; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.connection_status_label)

        # Offline queue label
        self.offline_queue_label = QLabel("큐: 0")
        self.offline_queue_label.setObjectName("offline_queue_label")
        self.offline_queue_label.setStyleSheet("padding: 0 10px;")
        self.offline_queue_label.setVisible(False)
        self.status_bar.addPermanentWidget(self.offline_queue_label)

        # Manual retry button
        self.retry_button = QPushButton("재시도")
        self.retry_button.setObjectName("retry_button")
        self.retry_button.setStyleSheet("padding: 2px 10px;")
        self.retry_button.clicked.connect(self.on_manual_retry)
        self.retry_button.setVisible(False)
        self.status_bar.addPermanentWidget(self.retry_button)

        self.status_bar.showMessage("준비")

    def create_header(self) -> QFrame:
        """Create top header bar (Supabase style)"""
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(64)

        # Theme background color
        theme = get_current_theme()
        if theme:
            bg_color = theme.get("colors.background.header", "#181818")
            border_color = theme.get("colors.border.sidebar", "#1a1a1a")
            header.setStyleSheet(f"""
                #header {{
                    background-color: {bg_color};
                    border-bottom: 1px solid {border_color};
                }}
            """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(20)

        # Left spacer
        layout.addStretch()

        # Logo/Title (Center)
        logo_label = QLabel("F2X NeuroHub MES")
        logo_label.setAlignment(Qt.AlignCenter)
        theme = get_current_theme()
        text_color = theme.get("colors.text.onDark", "#ffffff") if theme else "#ffffff"
        logo_label.setStyleSheet(f"""
            color: {text_color};
            font-size: 18px;
            font-weight: 700;
            padding: 0;
        """)
        layout.addWidget(logo_label)

        # Right spacer
        layout.addStretch()

        # Connection Status (Right)
        conn_status_container = QWidget()
        conn_status_layout = QHBoxLayout(conn_status_container)
        conn_status_layout.setContentsMargins(0, 0, 0, 0)
        conn_status_layout.setSpacing(8)

        status_icon = QLabel("🟢")
        status_icon.setStyleSheet("font-size: 14px;")
        conn_status_layout.addWidget(status_icon)

        status_text = QLabel("온라인")
        theme = get_current_theme()
        brand_color = theme.get("colors.brand.main", "#3ECF8E") if theme else "#3ECF8E"
        status_text.setStyleSheet(f"color: {brand_color}; font-size: 13px; font-weight: 500;")
        conn_status_layout.addWidget(status_text)

        layout.addWidget(conn_status_container)

        # Login Button (Right)
        theme = get_current_theme()
        icon_dark_color = theme.get("colors.text.primary", "#212121") if theme else "#212121"
        login_icon = create_icon("login", icon_dark_color, 16)
        login_btn = LoginButton(text="Sign In", icon=login_icon, on_click=self.on_login)
        layout.addWidget(login_btn.get_widget())

        return header

    def on_login(self):
        """Handle login button click"""
        QMessageBox.information(self, "로그인", "로그인 기능은 데모 모드에서 비활성화되어 있습니다.")

    def create_sidebar(self) -> QFrame:
        """Create sidebar navigation"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(Layout.SIDEBAR_WIDTH)

        # Theme background color
        theme = get_current_theme()
        if theme:
            bg_color = theme.get("colors.background.sidebar", "#263238")
            border_color = theme.get("colors.border.sidebar", "#1a1a1a")
            sidebar.setStyleSheet(f"""
                #sidebar {{
                    background-color: {bg_color};
                    border-right: 1px solid {border_color};
                }}
            """)

        layout = QVBoxLayout(sidebar)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 16, 12, 16)

        # Get theme colors for icons
        theme = get_current_theme()
        icon_color = theme.get('colors.text.sidebarSecondary', '#b0bec5') if theme else '#b0bec5'

        # Hamburger button
        hamburger_icon = create_icon("menu", icon_color, 24)
        self.hamburger_button = QPushButton()
        self.hamburger_button.setObjectName("hamburger_button")
        self.hamburger_button.setIcon(hamburger_icon)
        self.hamburger_button.setIconSize(QSize(24, 24))
        self.hamburger_button.setCursor(Qt.PointingHandCursor)
        self.hamburger_button.setFixedSize(40, 40)
        self.hamburger_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
        """)
        self.hamburger_button.clicked.connect(self.toggle_sidebar)
        layout.addWidget(self.hamburger_button)

        layout.addSpacing(20)

        # Navigation buttons - Flat Menu Structure
        icon_active_color = theme.get('colors.brand.main', '#3ECF8E') if theme else '#3ECF8E'

        # Main navigation items
        main_nav_items = [
            ("dashboard", "대시보드", 0, "dashboard"),
            ("process", "공정 작업", 1, "tool"),
            ("history", "작업 이력", 2, "history"),
            ("stats", "통계", 3, "chart"),
            ("settings", "설정", 4, "settings"),
        ]

        for key, text, page_index, icon_name in main_nav_items:
            icon = create_icon(icon_name, icon_active_color if page_index == 0 else icon_color)
            btn = SidebarButton(text=text, icon=icon, is_active=(page_index == 0))
            btn_widget = btn.get_widget()
            btn_widget.clicked.connect(lambda idx=page_index: self.switch_page(idx))
            self.nav_buttons[page_index] = btn
            layout.addWidget(btn_widget)

        # Spacer between settings and system actions
        layout.addStretch()

        # System action items
        system_items = [
            ("refresh", "새로고침", -1, "refresh"),
            ("about", "정보", -2, "info"),
            ("exit", "종료", -3, "logout"),
        ]

        for key, text, page_index, icon_name in system_items:
            icon = create_icon(icon_name, icon_color)
            btn = SidebarButton(text=text, icon=icon, is_active=False)
            btn_widget = btn.get_widget()

            if page_index == -1:
                # Refresh
                btn_widget.clicked.connect(self.on_refresh)
            elif page_index == -2:
                # About
                btn_widget.clicked.connect(self.on_about)
            elif page_index == -3:
                # Exit
                btn_widget.clicked.connect(self.close)

            layout.addWidget(btn_widget)

        # Spacer to push user info to bottom
        layout.addStretch()

        # User info at bottom
        user_name = "Unknown"
        if self.app_state.current_user:
            user_name = self.app_state.current_user.get('username', 'Unknown')

        # Get theme colors for sidebar text
        theme = get_current_theme()
        sidebar_text_secondary = theme.get('colors.text.sidebarSecondary', '#b0bec5') if theme else '#b0bec5'
        sidebar_text_tertiary = theme.get('colors.text.sidebarTertiary', '#90a4ae') if theme else '#90a4ae'

        self.user_label = QLabel(f"{user_name}")
        self.user_label.setObjectName("user_label")
        self.user_label.setStyleSheet(f"color: {sidebar_text_secondary}; font-size: 12px; padding: 8px;")
        layout.addWidget(self.user_label)

        # Process info at bottom
        self.process_label = QLabel(f"공정 {self.config.process_number}\n{self.config.process_name}")
        self.process_label.setObjectName("process_label")
        self.process_label.setStyleSheet(f"color: {sidebar_text_tertiary}; font-size: 11px; padding: 4px 8px;")
        self.process_label.setWordWrap(True)
        layout.addWidget(self.process_label)

        return sidebar

    def create_dashboard_view(self) -> QWidget:
        """Create dashboard view (Page 0)"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Title
        title_label = QLabel("대시보드")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("실시간 공정 현황")
        theme = get_current_theme()
        subtitle_color = theme.get("colors.text.secondary", "#757575") if theme else "#757575"
        subtitle_label.setStyleSheet(f"color: {subtitle_color}; font-size: 14px;")
        layout.addWidget(subtitle_label)

        layout.addSpacing(12)

        # Stats cards in horizontal layout
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)

        stats_items = [
            ('today_started', '금일 착공', '0', 'success'),
            ('today_completed', '금일 완공', '0', 'completed'),
            ('today_passed', '합격', '0', 'success'),
            ('today_failed', '불합격', '0', 'danger'),
            ('in_progress', '진행중', '0', 'inProgress')
        ]

        for key, label_text, initial_value, variant in stats_items:
            stat_card = StatCard(label_text=label_text, value=initial_value, variant=variant)
            stats_layout.addWidget(stat_card.get_widget())
            self.stat_cards[key] = stat_card

        layout.addLayout(stats_layout)

        # Content area placeholder
        content_label = QLabel("공정 관리 화면")
        content_label.setAlignment(Qt.AlignCenter)
        theme = get_current_theme()
        placeholder_color = theme.get("colors.text.placeholder", "#999999") if theme else "#999999"
        content_label.setStyleSheet(f"font-size: 18px; color: {placeholder_color}; padding: 48px;")
        layout.addWidget(content_label, 1)

        return container

    def create_process_view(self) -> QWidget:
        """Create process work view (Page 1)"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)

        title_label = QLabel("공정 작업")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        content_label = QLabel("공정 작업 화면 (개발 예정)")
        content_label.setAlignment(Qt.AlignCenter)
        theme = get_current_theme()
        placeholder_color = theme.get("colors.text.placeholder", "#999999") if theme else "#999999"
        content_label.setStyleSheet(f"font-size: 16px; color: {placeholder_color}; padding: 48px;")
        layout.addWidget(content_label, 1)

        return container

    def create_history_view(self) -> QWidget:
        """Create history view (Page 2)"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)

        title_label = QLabel("작업 이력")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        content_label = QLabel("작업 이력은 Ctrl+H 또는 메뉴에서 조회하세요")
        content_label.setAlignment(Qt.AlignCenter)
        theme = get_current_theme()
        placeholder_color = theme.get("colors.text.placeholder", "#999999") if theme else "#999999"
        content_label.setStyleSheet(f"font-size: 16px; color: {placeholder_color}; padding: 48px;")
        layout.addWidget(content_label, 1)

        return container

    def create_stats_view(self) -> QWidget:
        """Create statistics view (Page 3)"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)

        title_label = QLabel("통계")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        content_label = QLabel("통계 화면 (개발 예정)")
        content_label.setAlignment(Qt.AlignCenter)
        theme = get_current_theme()
        placeholder_color = theme.get("colors.text.placeholder", "#999999") if theme else "#999999"
        content_label.setStyleSheet(f"font-size: 16px; color: {placeholder_color}; padding: 48px;")
        layout.addWidget(content_label, 1)

        return container

    def create_settings_view(self) -> QWidget:
        """Create settings view (Page 4)"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)

        title_label = QLabel("설정")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        content_label = QLabel("환경설정 화면 (개발 예정)")
        content_label.setAlignment(Qt.AlignCenter)
        theme = get_current_theme()
        placeholder_color = theme.get("colors.text.placeholder", "#999999") if theme else "#999999"
        content_label.setStyleSheet(f"font-size: 16px; color: {placeholder_color}; padding: 48px;")
        layout.addWidget(content_label, 1)

        return container

    def switch_page(self, page_index: int):
        """Switch to different page"""
        if page_index == self.current_page_index:
            return

        # Update navigation buttons
        if self.current_page_index in self.nav_buttons:
            self.nav_buttons[self.current_page_index].set_active(False)

        if page_index in self.nav_buttons:
            self.nav_buttons[page_index].set_active(True)

        # Switch page
        self.content_stack.setCurrentIndex(page_index)
        self.current_page_index = page_index

        # Update status bar
        page_names = ["대시보드", "공정 작업", "작업 이력", "통계", "설정"]
        if 0 <= page_index < len(page_names):
            self.status_bar.showMessage(f"{page_names[page_index]} 화면", 2000)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Ctrl+Q: Exit
        exit_shortcut = QAction(self)
        exit_shortcut.setShortcut("Ctrl+Q")
        exit_shortcut.triggered.connect(self.close)
        self.addAction(exit_shortcut)

        # F5: Refresh
        refresh_shortcut = QAction(self)
        refresh_shortcut.setShortcut("F5")
        refresh_shortcut.triggered.connect(self.on_refresh)
        self.addAction(refresh_shortcut)

        # Ctrl+H: History
        history_shortcut = QAction(self)
        history_shortcut.setShortcut("Ctrl+H")
        history_shortcut.triggered.connect(self.on_show_history)
        self.addAction(history_shortcut)

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
        for key, stat_card in self.stat_cards.items():
            value = stats.get(key, 0)
            stat_card.set_value(str(value))

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
        # Switch to settings page
        self.switch_page(4)

    def on_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "F2X NeuroHub MES 정보",
            "F2X NeuroHub MES\n"
            "공정 관리 시스템\n\n"
            f"현재 공정: {self.config.process_name}\n"
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

    def toggle_sidebar(self):
        """Toggle sidebar expand/collapse with smooth animation"""
        if self.sidebar_expanded:
            # Collapse sidebar
            target_width = 60
            self.sidebar_expanded = False

            # Hide text labels (logo_label removed, only user/process labels)
            self.user_label.setVisible(False)
            self.process_label.setVisible(False)

            # Hide button text by updating all buttons to icon-only mode
            for btn_obj in self.nav_buttons.values():
                widget = btn_obj.get_widget()
                widget.setText("")
        else:
            # Expand sidebar
            target_width = Layout.SIDEBAR_WIDTH
            self.sidebar_expanded = True

            # Show text labels (logo_label removed, only user/process labels)
            self.user_label.setVisible(True)
            self.process_label.setVisible(True)

            # Restore button text
            nav_items = [
                (0, "대시보드"),
                (1, "공정 작업"),
                (2, "작업 이력"),
                (3, "통계"),
                (4, "설정")
            ]
            for page_index, text in nav_items:
                if page_index in self.nav_buttons:
                    self.nav_buttons[page_index].get_widget().setText(text)

        # Create animation group for smooth parallel animations
        self.sidebar_animation_group = QParallelAnimationGroup()

        # Animate minimum width
        self.sidebar_min_animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.sidebar_min_animation.setDuration(350)
        self.sidebar_min_animation.setStartValue(self.sidebar.width())
        self.sidebar_min_animation.setEndValue(target_width)
        self.sidebar_min_animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.sidebar_animation_group.addAnimation(self.sidebar_min_animation)

        # Animate maximum width
        self.sidebar_max_animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.sidebar_max_animation.setDuration(350)
        self.sidebar_max_animation.setStartValue(self.sidebar.width())
        self.sidebar_max_animation.setEndValue(target_width)
        self.sidebar_max_animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.sidebar_animation_group.addAnimation(self.sidebar_max_animation)

        # Start the animation group
        self.sidebar_animation_group.start()

    def closeEvent(self, event):
        """Handle window close event - cleanup threads"""
        import logging
        logger = logging.getLogger(__name__)

        logger.info("MainWindow closing - cleaning up resources...")

        # Clean up ViewModel workers
        if hasattr(self.viewmodel, 'cleanup_workers'):
            self.viewmodel.cleanup_workers()

        # Clean up RetryManager worker
        if hasattr(self.viewmodel, 'retry_manager') and self.viewmodel.retry_manager:
            if hasattr(self.viewmodel.retry_manager, 'cleanup'):
                self.viewmodel.retry_manager.cleanup()

        # Save window geometry
        self.config.window_geometry = self.saveGeometry()

        logger.info("MainWindow cleanup completed")
        event.accept()
