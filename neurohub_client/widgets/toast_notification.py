"""
Toast Notification Widget - Non-blocking popup notifications.

Displays temporary messages at the top center of the parent window.
Uses Property Variants for styling via app-level QSS.
"""
import logging
from typing import Optional

from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QWidget
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QFont

logger = logging.getLogger(__name__)


class Toast(QFrame):
    """Toast notification popup using Property Variant styling."""

    # Class-level list to track active toasts for stacking
    _active_toasts: list = []

    def __init__(
        self,
        parent: QWidget,
        message: str,
        variant: str = "toast",
        duration: int = 3000
    ):
        """
        Initialize Toast notification.

        Args:
            parent: Parent widget (usually MainWindow)
            message: Message to display
            variant: Toast variant (toast, toast-success, toast-danger,
                     toast-warning, toast-info)
            duration: Display duration in milliseconds (0 for persistent)
        """
        super().__init__(parent)
        self.message = message
        self.duration = duration

        # Set Property Variant for QSS styling
        self.setProperty("variant", variant)

        # Window flags for overlay behavior
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        self._setup_ui()

        # Add to active toasts
        Toast._active_toasts.append(self)

        # Position and animate
        self._position_toast()
        self._slide_in()

        # Auto-hide timer
        if duration > 0:
            QTimer.singleShot(duration, self._slide_out)

    def _setup_ui(self):
        """Setup UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Message label
        self.label = QLabel(self.message)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)

        # Inherit font from parent
        font = QFont()
        font.setPointSize(11)
        font.setWeight(QFont.Medium)
        self.label.setFont(font)

        layout.addWidget(self.label)

        # Set minimum/maximum size
        self.setMinimumWidth(200)
        self.setMaximumWidth(350)
        self.adjustSize()

    def _position_toast(self):
        """Position toast at top center of parent window."""
        if not self.parent():
            return

        parent = self.parent()
        parent_rect = parent.rect()

        # Calculate position (top center)
        toast_width = self.sizeHint().width()
        toast_height = self.sizeHint().height()

        x = (parent_rect.width() - toast_width) // 2
        y = 20  # 20px from top

        # Stack multiple toasts
        index = Toast._active_toasts.index(self) if self in Toast._active_toasts else 0
        y += index * (toast_height + 10)

        # Convert to global screen coordinates (required for Tool windows)
        global_pos = parent.mapToGlobal(QPoint(x, y))
        self._target_pos = global_pos
        self.move(global_pos)

    def _slide_in(self):
        """Slide in animation from top."""
        if not self.parent():
            return

        # Start position (above the target)
        start_pos = QPoint(self._target_pos.x(), self._target_pos.y() - 50)
        self.move(start_pos)

        # Animate to target position
        self._slide_anim = QPropertyAnimation(self, b"pos")
        self._slide_anim.setDuration(250)
        self._slide_anim.setStartValue(start_pos)
        self._slide_anim.setEndValue(self._target_pos)
        self._slide_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._slide_anim.start()

    def _slide_out(self):
        """Slide out animation to top."""
        if not self.parent():
            self._close_toast()
            return

        # Animate upward and out
        current_pos = self.pos()
        end_pos = QPoint(current_pos.x(), current_pos.y() - 50)

        self._slide_anim = QPropertyAnimation(self, b"pos")
        self._slide_anim.setDuration(200)
        self._slide_anim.setStartValue(current_pos)
        self._slide_anim.setEndValue(end_pos)
        self._slide_anim.setEasingCurve(QEasingCurve.InCubic)
        self._slide_anim.finished.connect(self._close_toast)
        self._slide_anim.start()

    def _close_toast(self):
        """Close and cleanup toast."""
        if self in Toast._active_toasts:
            Toast._active_toasts.remove(self)
            # Reposition remaining toasts
            for i, toast in enumerate(Toast._active_toasts):
                toast._reposition(i)
        self.close()
        self.deleteLater()

    def _reposition(self, index: int):
        """Reposition toast based on index in stack."""
        if not self.parent():
            return

        parent = self.parent()
        parent_rect = parent.rect()

        toast_width = self.width()
        toast_height = self.height()

        x = (parent_rect.width() - toast_width) // 2
        y = 20 + index * (toast_height + 10)

        # Convert to global screen coordinates
        global_pos = parent.mapToGlobal(QPoint(x, y))
        self.move(global_pos)

    def mousePressEvent(self, event):
        """Close toast on click."""
        self._close_toast()
        super().mousePressEvent(event)

    # Static convenience methods
    @staticmethod
    def success(parent: QWidget, message: str, duration: int = 3000) -> 'Toast':
        """
        Show success toast.

        Args:
            parent: Parent widget
            message: Message to display
            duration: Display duration in ms

        Returns:
            Toast instance
        """
        toast = Toast(parent, message, "toast-success", duration)
        toast.show()
        return toast

    @staticmethod
    def danger(parent: QWidget, message: str, duration: int = 4000) -> 'Toast':
        """
        Show danger/error toast.

        Args:
            parent: Parent widget
            message: Message to display
            duration: Display duration in ms

        Returns:
            Toast instance
        """
        toast = Toast(parent, message, "toast-danger", duration)
        toast.show()
        return toast

    @staticmethod
    def warning(parent: QWidget, message: str, duration: int = 3500) -> 'Toast':
        """
        Show warning toast.

        Args:
            parent: Parent widget
            message: Message to display
            duration: Display duration in ms

        Returns:
            Toast instance
        """
        toast = Toast(parent, message, "toast-warning", duration)
        toast.show()
        return toast

    @staticmethod
    def info(parent: QWidget, message: str, duration: int = 3000) -> 'Toast':
        """
        Show info toast.

        Args:
            parent: Parent widget
            message: Message to display
            duration: Display duration in ms

        Returns:
            Toast instance
        """
        toast = Toast(parent, message, "toast-info", duration)
        toast.show()
        return toast

    @staticmethod
    def clear_all():
        """Clear all active toasts."""
        for toast in Toast._active_toasts[:]:
            toast._close_toast()
