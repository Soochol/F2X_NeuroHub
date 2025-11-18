"""Login Dialog - User authentication dialog"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from services.auth_service import AuthService
from config import AppConfig


class LoginDialog(QDialog):
    """User authentication dialog"""

    def __init__(self, auth_service: AuthService, config: AppConfig, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.config = config
        self.setWindowTitle("F2X NeuroHub MES - 로그인")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setup_ui()
        self.load_saved_credentials()

    def setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("F2X NeuroHub MES")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("공정 관리 시스템")
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)

        layout.addSpacing(20)

        # Username
        username_label = QLabel("사용자 ID:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("사용자 ID를 입력하세요")
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)

        # Password
        password_label = QLabel("비밀번호:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("비밀번호를 입력하세요")
        self.password_input.returnPressed.connect(self.on_login)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)

        # Auto-login checkbox
        self.auto_login_checkbox = QCheckBox("자동 로그인")
        self.auto_login_checkbox.setChecked(self.config.auto_login_enabled)
        layout.addWidget(self.auto_login_checkbox)

        # Error message
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setWordWrap(True)
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

        layout.addSpacing(10)

        # Buttons
        button_layout = QHBoxLayout()
        self.login_button = QPushButton("로그인")
        self.login_button.clicked.connect(self.on_login)
        self.login_button.setDefault(True)

        self.cancel_button = QPushButton("취소")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_saved_credentials(self):
        """Load saved username if auto-login is enabled"""
        if self.config.auto_login_enabled:
            saved_username = self.config.saved_username
            if saved_username:
                self.username_input.setText(saved_username)
                self.password_input.setFocus()

    def on_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        # Validation
        if not username:
            self.show_error("사용자 ID를 입력하세요")
            return

        if not password:
            self.show_error("비밀번호를 입력하세요")
            return

        # Disable button during login
        self.login_button.setEnabled(False)
        self.login_button.setText("로그인 중...")
        self.error_label.setText("")

        # Attempt login
        if self.auth_service.login(username, password):
            # Save settings
            self.config.auto_login_enabled = self.auto_login_checkbox.isChecked()
            if self.config.auto_login_enabled:
                self.config.saved_username = username
                self.config.saved_token = self.auth_service.access_token
            else:
                self.config.saved_username = ""
                self.config.saved_token = ""

            self.accept()  # Close dialog with success
        else:
            # Re-enable button
            self.login_button.setEnabled(True)
            self.login_button.setText("로그인")
            self.show_error("로그인 실패: 사용자 ID 또는 비밀번호를 확인하세요")

    def show_error(self, message: str):
        """Show error message"""
        self.error_label.setText(message)