"""
Login Dialog for authentication.
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                               QPushButton, QCheckBox, QMessageBox)
from PySide6.QtCore import Qt
from widgets.base_components import ThemedLabel
import logging

logger = logging.getLogger(__name__)


class LoginDialog(QDialog):
    """Login dialog for user authentication."""

    def __init__(self, auth_service, config, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.config = config
        self.setWindowTitle("로그인")
        self.setModal(True)
        self.resize(350, 250)
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = ThemedLabel("F2X NeuroHub 공정 추적", variant="heading")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Username
        username_label = ThemedLabel("사용자명:", variant="body")
        layout.addWidget(username_label)
        self.username_input = QLineEdit()
        self.username_input.setObjectName("username_input")
        self.username_input.setPlaceholderText("사용자명을 입력하세요")
        if self.config.saved_username:
            self.username_input.setText(self.config.saved_username)
        layout.addWidget(self.username_input)

        # Password
        password_label = ThemedLabel("비밀번호:", variant="body")
        layout.addWidget(password_label)
        self.password_input = QLineEdit()
        self.password_input.setObjectName("password_input")
        self.password_input.setPlaceholderText("비밀번호를 입력하세요")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

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
        self.username_input.returnPressed.connect(self.on_login)
        self.password_input.returnPressed.connect(self.on_login)

    def connect_signals(self):
        """Connect auth service signals."""
        self.auth_service.login_success.connect(self.on_login_success)
        self.auth_service.auth_error.connect(self.on_login_error)

    def on_login(self):
        """Handle login button click (initiates threaded login)."""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "입력 오류", "사용자명과 비밀번호를 모두 입력해주세요.")
            return

        # Disable button while login in progress
        self.login_button.setEnabled(False)
        self.login_button.setText("로그인 중...")
        logger.info(f"Initiating threaded login for user: {username}")

        # Initiate threaded login
        self.auth_service.login(username, password)

    def on_login_success(self, user_data: dict):
        """Handle successful login from threaded operation."""
        username = user_data.get('username', 'UNKNOWN')
        logger.info(f"Login successful (dialog): {username}")

        # Save credentials if auto-login enabled
        if self.auto_login_check.isChecked():
            self.config.saved_username = username
            self.config.saved_token = self.auth_service.access_token
            self.config.auto_login_enabled = True
        else:
            self.config.auto_login_enabled = False

        # Re-enable button
        self.login_button.setEnabled(True)
        self.login_button.setText("로그인")

        # Close dialog
        self.accept()

    def on_login_error(self, error_msg: str):
        """Handle login error from threaded operation."""
        logger.error(f"Login error (dialog): {error_msg}")

        # Re-enable button
        self.login_button.setEnabled(True)
        self.login_button.setText("로그인")

        # Show error message
        QMessageBox.critical(self, "로그인 실패", error_msg)
