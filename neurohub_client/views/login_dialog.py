"""
Login Dialog for authentication.
"""
import logging
from typing import Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QLineEdit, QMessageBox, QPushButton,
    QVBoxLayout, QWidget
)

from utils.exception_handler import SignalConnector, safe_slot
from widgets.base_components import ThemedLabel

logger = logging.getLogger(__name__)


class LoginDialog(QDialog):
    """Login dialog for user authentication."""

    def __init__(self, auth_service: Any, config: Any, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.auth_service = auth_service
        self.config = config
        self.setWindowTitle("로그인")
        self.setModal(True)
        self.resize(350, 250)
        # Prevent minimize, keep on top, only show close button
        self.setWindowFlags(
            Qt.Dialog |
            Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint |
            Qt.WindowStaysOnTopHint
        )
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self) -> None:
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = ThemedLabel("F2X NeuroHub 공정 추적", variant="heading")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Username (editable combobox with recent usernames)
        username_label = ThemedLabel("사용자명:", variant="body")
        layout.addWidget(username_label)
        self.username_input = QComboBox()
        self.username_input.setObjectName("username_input")
        self.username_input.setEditable(True)
        self.username_input.lineEdit().setPlaceholderText("사용자명을 입력하세요")
        # Style combobox for dark mode visibility
        self.username_input.setStyleSheet("""
            QComboBox {
                background-color: #2D2D2D;
                color: #E0E0E0;
                border: 1px solid #4A4A4A;
                border-radius: 4px;
                padding: 6px 10px;
                min-height: 20px;
            }
            QComboBox:hover {
                border-color: #5A5A5A;
            }
            QComboBox:focus {
                border-color: #3B82F6;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid #4A4A4A;
                background-color: #3A3A3A;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #B0B0B0;
                margin-right: 5px;
            }
            QComboBox::down-arrow:hover {
                border-top-color: #FFFFFF;
            }
            QComboBox QAbstractItemView {
                background-color: #2D2D2D;
                color: #E0E0E0;
                border: 1px solid #4A4A4A;
                selection-background-color: #3B82F6;
                selection-color: white;
            }
        """)
        # Populate with recent usernames
        recent_usernames = self.config.recent_usernames
        if recent_usernames:
            self.username_input.addItems(recent_usernames)
        # Set saved username as current text
        if self.config.saved_username:
            self.username_input.setCurrentText(self.config.saved_username)
        layout.addWidget(self.username_input)

        # Password
        password_label = ThemedLabel("비밀번호:", variant="body")
        layout.addWidget(password_label)
        self.password_input = QLineEdit()
        self.password_input.setObjectName("password_input")
        self.password_input.setPlaceholderText("비밀번호를 입력하세요")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Set focus to password field if username was pre-filled
        if self.config.saved_username:
            self.password_input.setFocus()

        # Auto-login checkbox
        self.auto_login_check = QCheckBox("자동 로그인")
        self.auto_login_check.setChecked(self.config.auto_login_enabled)
        layout.addWidget(self.auto_login_check)

        # Login button
        self.login_button = QPushButton("로그인")
        self.login_button.setObjectName("login_button")
        self.login_button.setProperty("variant", "primary")
        self.login_button.clicked.connect(self.on_login)
        layout.addWidget(self.login_button)

        # Connect Enter key to login
        self.username_input.lineEdit().returnPressed.connect(self.on_login)
        self.password_input.returnPressed.connect(self.on_login)

    def connect_signals(self) -> None:
        """Connect auth service signals."""
        connector = SignalConnector()
        connector.connect(
            self.auth_service.login_success,
            self.on_login_success,
            "login_success -> on_login_success"
        ).connect(
            self.auth_service.auth_error,
            self.on_login_error,
            "auth_error -> on_login_error"
        )

        if not connector.all_connected():
            logger.error(
                f"로그인 시그널 연결 실패: {connector.failed_connections}"
            )

    def on_login(self) -> None:
        """Handle login button click (initiates threaded login)."""
        username = self.username_input.currentText().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "입력 오류", "사용자명과 비밀번호를 모두 입력해주세요.")
            return

        # Disable inputs and button while login in progress
        self.username_input.setEnabled(False)
        self.password_input.setEnabled(False)
        self.login_button.setEnabled(False)
        self.login_button.setText("로그인 중...")
        logger.info(f"Initiating threaded login for user: {username}")

        # Initiate threaded login
        self.auth_service.login(username, password)

    @safe_slot("로그인 성공 처리 실패", show_dialog=True)
    def on_login_success(self, user_data: dict) -> None:
        """Handle successful login from threaded operation."""
        username = user_data.get('username', 'UNKNOWN')
        logger.info(f"Login successful (dialog): {username}")

        # Always save last login username (for auto-fill on next login)
        self.config.saved_username = username
        # Add to recent usernames list
        self.config.add_recent_username(username)

        # Save token only if auto-login enabled
        if self.auto_login_check.isChecked():
            self.config.saved_token = self.auth_service.access_token
            self.config.auto_login_enabled = True
            logger.info("Auto-login enabled")
        else:
            self.config.auto_login_enabled = False
            logger.info("Auto-login disabled")

        # Re-enable inputs and button
        self.username_input.setEnabled(True)
        self.password_input.setEnabled(True)
        self.login_button.setEnabled(True)
        self.login_button.setText("로그인")

        # Close dialog
        self.accept()

    @safe_slot("로그인 에러 처리 실패")
    def on_login_error(self, error_msg: str) -> None:
        """Handle login error from threaded operation."""
        logger.error(f"Login error (dialog): {error_msg}")

        # Re-enable inputs and button
        self.username_input.setEnabled(True)
        self.password_input.setEnabled(True)
        self.login_button.setEnabled(True)
        self.login_button.setText("로그인")

        # Show error message
        QMessageBox.critical(self, "로그인 실패", error_msg)
