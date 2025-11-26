"""
Error Banner Widget - Displays last error at bottom of page.
"""
from datetime import datetime
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget

from utils.theme_manager import get_theme

theme = get_theme()


class ErrorBanner(QFrame):
    """
    Error banner that displays at the bottom of a page.

    Shows the most recent error with timestamp and close button.
    Auto-clears when work starts/completes.
    """

    dismissed = Signal()  # Emitted when user closes the banner

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("error_banner")
        self._setup_ui()
        self.hide()  # Initially hidden

    def _setup_ui(self) -> None:
        """Setup UI components."""
        # Colors
        danger_main = theme.get('colors.danger.main')
        danger_dark = theme.get('colors.danger.dark')
        text_on_dark = theme.get('colors.text.on_dark')

        self.setStyleSheet(f"""
            #error_banner {{
                background-color: {danger_main};
                border-radius: 6px;
                padding: 8px 12px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # Error icon
        icon_label = QLabel("\u26a0")  # Warning sign
        icon_label.setStyleSheet(f"color: {text_on_dark}; font-size: 16px;")
        layout.addWidget(icon_label)

        # Error message
        self.message_label = QLabel("")
        self.message_label.setStyleSheet(f"""
            color: {text_on_dark};
            font-size: 13px;
            font-weight: 500;
        """)
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label, stretch=1)

        # Timestamp
        self.time_label = QLabel("")
        self.time_label.setStyleSheet(f"""
            color: rgba(255, 255, 255, 0.7);
            font-size: 11px;
        """)
        layout.addWidget(self.time_label)

        # Close button
        close_btn = QPushButton("\u2715")  # X symbol
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {text_on_dark};
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 12px;
            }}
        """)
        close_btn.clicked.connect(self.clear)
        layout.addWidget(close_btn)

    def show_error(self, message: str) -> None:
        """
        Show error message with current timestamp.

        Args:
            message: Error message to display
        """
        self.message_label.setText(message)
        self.time_label.setText(datetime.now().strftime("%H:%M:%S"))
        self.show()

    def clear(self) -> None:
        """Clear and hide the error banner."""
        self.message_label.setText("")
        self.time_label.setText("")
        self.hide()
        self.dismissed.emit()

    def is_showing(self) -> bool:
        """Check if banner is currently visible."""
        return self.isVisible()
