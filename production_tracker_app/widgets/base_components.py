"""
Base Components - Reusable themed UI components using Property Variants.

Components use setProperty("variant", ...) for styling via app-level QSS.
"""
import logging
from typing import Optional

from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt
from utils.theme_manager import get_theme

logger = logging.getLogger(__name__)
theme = get_theme()


class ThemedCard(QFrame):
    """Base themed card component using Property Variant."""

    def __init__(self, min_height: int = 120, variant: str = "card", parent=None):
        """
        Initialize themed card.

        Args:
            min_height: Minimum height in pixels
            variant: Card variant ("card", "elevated")
            parent: Parent widget
        """
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setMinimumHeight(min_height)
        self.setProperty("variant", variant)


class ThemedLabel(QLabel):
    """Base themed label component using Property Variant."""

    def __init__(self, text: str = "", variant: str = "body", parent=None):
        """
        Initialize themed label.

        Args:
            text: Label text
            variant: Label variant ("title", "body", "caption",
                     "success", "danger", "warning", "brand")
            parent: Parent widget
        """
        super().__init__(text, parent)
        self.setProperty("variant", variant)

    def set_variant(self, variant: str):
        """
        Update label variant dynamically.

        Args:
            variant: New variant name
        """
        self.setProperty("variant", variant)
        self.style().unpolish(self)
        self.style().polish(self)


class ThemedButton(QPushButton):
    """Base themed button component using Property Variant."""

    def __init__(self, text: str = "", variant: str = "primary", parent=None):
        """
        Initialize themed button.

        Args:
            text: Button text
            variant: Button variant ("primary", "secondary", "danger", "ghost")
            parent: Parent widget
        """
        super().__init__(text, parent)
        self.setProperty("variant", variant)

    def set_variant(self, variant: str):
        """
        Update button variant dynamically.

        Args:
            variant: New variant name
        """
        self.setProperty("variant", variant)
        self.style().unpolish(self)
        self.style().polish(self)


class StatusIndicator(QLabel):
    """Status indicator component with color coding using Property Variant."""

    def __init__(self, text: str = "", status: str = "body", parent=None):
        """
        Initialize status indicator.

        Args:
            text: Status text
            status: Status type ("success", "danger", "warning", "body")
            parent: Parent widget
        """
        super().__init__(text, parent)
        self.setProperty("variant", status)

    def set_status(self, status: str, text: Optional[str] = None):
        """
        Update status.

        Args:
            status: New status ("success", "danger", "warning", "body")
            text: Optional new text
        """
        if text:
            self.setText(text)
        self.setProperty("variant", status)
        self.style().unpolish(self)
        self.style().polish(self)


class InfoCard(ThemedCard):
    """Information display card with title."""

    def __init__(self, title: str, min_height: int = 120, parent=None):
        """
        Initialize info card.

        Args:
            title: Card title
            min_height: Minimum height in pixels
            parent: Parent widget
        """
        super().__init__(min_height, "card", parent)
        self.title = title
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)

        spacing = theme.get('spacing.lg', 24)
        layout.setSpacing(spacing)

        margin = theme.get('spacing.md', 16)
        layout.setContentsMargins(margin, margin, margin, margin)

        # Title
        self.title_label = ThemedLabel(self.title, variant="title")
        layout.addWidget(self.title_label)

        # Content area (to be populated by subclasses)
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)


class StatBadge(QLabel):
    """Statistic display badge with background."""

    def __init__(self, name: str, value: str, variant: str = "body", parent=None):
        """
        Initialize stat badge.

        Args:
            name: Stat name
            value: Stat value
            variant: Badge variant ("success", "danger", "warning", "brand")
            parent: Parent widget
        """
        super().__init__(f"{name}: {value}", parent)
        self.stat_name = name
        self.stat_value = value
        self.setProperty("variant", variant)
        self.setAlignment(Qt.AlignCenter)

    def update_value(self, value: str):
        """
        Update stat value.

        Args:
            value: New value
        """
        self.stat_value = value
        self.setText(f"{self.stat_name}: {value}")

    def set_variant(self, variant: str):
        """
        Update badge variant.

        Args:
            variant: New variant name
        """
        self.setProperty("variant", variant)
        self.style().unpolish(self)
        self.style().polish(self)
