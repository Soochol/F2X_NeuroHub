"""
Base Components - Reusable themed UI components.

Centralized collection of styled components that use the theme system.
"""
from PySide6.QtWidgets import QFrame, QLabel, QPushButton
from PySide6.QtCore import Qt
from utils.theme_manager import get_theme
import logging

logger = logging.getLogger(__name__)
theme = get_theme()


class ThemedCard(QFrame):
    """Base themed card component."""

    def __init__(self, min_height: int = 120, parent=None):
        """
        Initialize themed card.

        Args:
            min_height: Minimum height in pixels
            parent: Parent widget
        """
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setMinimumHeight(min_height)
        self._apply_theme()

    def _apply_theme(self):
        """Apply theme styling to card."""
        card_style = theme.get_component_style('card')
        stylesheet = f"""
            QFrame {{
                background-color: {card_style.get('backgroundColor', '#2a2a2a')};
                border: {card_style.get('border', '1px solid #3a3a3a')};
                border-radius: {card_style.get('borderRadius', '8px')};
                padding: {card_style.get('padding', '15px')};
            }}
        """
        self.setStyleSheet(stylesheet)


class ThemedLabel(QLabel):
    """Base themed label component."""

    def __init__(self, text: str = "", style_type: str = "base", parent=None):
        """
        Initialize themed label.

        Args:
            text: Label text
            style_type: Style type ('title', 'base', 'secondary', 'tertiary')
            parent: Parent widget
        """
        super().__init__(text, parent)
        self.style_type = style_type
        self._apply_theme()

    def _apply_theme(self):
        """Apply theme styling to label."""
        if self.style_type == "title":
            font_size = theme.get_font_size('lg')
            color = theme.get_color('text.primary')
            font_weight = theme.get('typography.fontWeight.bold', 'bold')
            stylesheet = f"""
                font-size: {font_size};
                font-weight: {font_weight};
                color: {color};
                padding-bottom: 8px;
            """
        elif self.style_type == "secondary":
            font_size = theme.get_font_size('base')
            color = theme.get_color('text.secondary')
            stylesheet = f"""
                font-size: {font_size};
                color: {color};
            """
        elif self.style_type == "tertiary":
            font_size = theme.get_font_size('sm')
            color = theme.get_color('text.tertiary')
            stylesheet = f"""
                font-size: {font_size};
                color: {color};
            """
        else:  # base
            font_size = theme.get_font_size('base')
            color = theme.get_color('text.primary')
            stylesheet = f"""
                font-size: {font_size};
                color: {color};
            """

        self.setStyleSheet(stylesheet)


class ThemedButton(QPushButton):
    """Base themed button component."""

    def __init__(self, text: str = "", button_type: str = "primary", parent=None):
        """
        Initialize themed button.

        Args:
            text: Button text
            button_type: Button type ('primary', 'secondary')
            parent: Parent widget
        """
        super().__init__(text, parent)
        self.button_type = button_type
        self._apply_theme()

    def _apply_theme(self):
        """Apply theme styling to button."""
        style = theme.get_component_style(f'button.{self.button_type}')

        bg_color = style.get('backgroundColor', '#3b82f6')
        hover_bg = style.get('hoverBackgroundColor', '#2563eb')
        color = style.get('color', '#ffffff')
        padding = style.get('padding', '10px')
        font_size = style.get('fontSize', '14px')
        font_weight = style.get('fontWeight', 'bold')
        border_radius = style.get('borderRadius', '4px')

        stylesheet = f"""
            QPushButton {{
                background-color: {bg_color};
                color: {color};
                padding: {padding};
                font-size: {font_size};
                font-weight: {font_weight};
                border-radius: {border_radius};
                border: none;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
            }}
        """
        self.setStyleSheet(stylesheet)


class StatusIndicator(QLabel):
    """Status indicator component with color coding."""

    def __init__(self, text: str = "", status: str = "idle", parent=None):
        """
        Initialize status indicator.

        Args:
            text: Status text
            status: Status type ('online', 'offline', 'idle')
            parent: Parent widget
        """
        super().__init__(text, parent)
        self.status = status
        self._apply_theme()

    def _apply_theme(self):
        """Apply theme styling based on status."""
        color = theme.get_color(f'status.{self.status}')
        font_weight = theme.get('typography.fontWeight.bold', 'bold')
        stylesheet = f"""
            color: {color};
            font-weight: {font_weight};
        """
        self.setStyleSheet(stylesheet)

    def set_status(self, status: str, text: str = None):
        """
        Update status.

        Args:
            status: New status ('online', 'offline', 'idle')
            text: Optional new text
        """
        self.status = status
        if text:
            self.setText(text)
        self._apply_theme()


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
        super().__init__(min_height, parent)
        self.title = title
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components."""
        from PySide6.QtWidgets import QVBoxLayout

        layout = QVBoxLayout(self)
        spacing = int(theme.get_spacing('lg').replace('px', ''))
        layout.setSpacing(spacing)

        margins = (
            int(theme.get_spacing('md').replace('px', '')),
            int(theme.get_spacing('md').replace('px', '')),
            int(theme.get_spacing('md').replace('px', '')),
            int(theme.get_spacing('md').replace('px', ''))
        )
        layout.setContentsMargins(*margins)

        # Title
        self.title_label = ThemedLabel(self.title, style_type="title")
        layout.addWidget(self.title_label)

        # Content area (to be populated by subclasses)
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)


class StatBadge(QLabel):
    """Statistic display badge with background."""

    def __init__(self, name: str, value: str, color: str, parent=None):
        """
        Initialize stat badge.

        Args:
            name: Stat name
            value: Stat value
            color: Badge color
            parent: Parent widget
        """
        super().__init__(f"{name}: {value}", parent)
        self.stat_name = name
        self.stat_value = value
        self.stat_color = color
        self._apply_theme()

    def _apply_theme(self):
        """Apply theme styling to badge."""
        stylesheet = theme.get_stats_card_stat_label_style(self.stat_color)
        self.setStyleSheet(stylesheet)
        self.setAlignment(Qt.AlignCenter)

    def update_value(self, value: str):
        """
        Update stat value.

        Args:
            value: New value
        """
        self.stat_value = value
        self.setText(f"{self.stat_name}: {value}")
