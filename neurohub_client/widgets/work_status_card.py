"""
Work Status Card Widget - Displays work state, timing, and progress.
"""
import logging
from datetime import datetime

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QFrame
from PySide6.QtCore import Qt, QTimer
from utils.theme_manager import get_theme

logger = logging.getLogger(__name__)
theme = get_theme()


class StatusBadge(QLabel):
    """Small badge for status display."""

    def __init__(self, text: str = "", status: str = "default"):
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        self._status = status
        self._apply_style()

    def _apply_style(self):
        """Apply style based on status."""
        if not theme:
            return

        bg_elevated = theme.get("colors.background.elevated", "#1f1f1f")
        brand_main = theme.get("colors.brand.main", "#3ECF8E")
        success_main = theme.get("colors.success.main", "#3ECF8E")
        danger_main = theme.get("colors.danger.main", "#F04438")
        text_secondary = theme.get("colors.text.secondary", "#a8a8a8")
        radius_sm = theme.get("radius.sm", 4)

        colors = {
            "default": (bg_elevated, text_secondary),
            "active": (f"{brand_main}40", brand_main),
            "success": (f"{success_main}40", success_main),
            "danger": (f"{danger_main}40", danger_main),
        }

        bg, fg = colors.get(self._status, colors["default"])
        self.setStyleSheet(f"""
            background-color: {bg};
            color: {fg};
            padding: 4px 8px;
            border-radius: {radius_sm}px;
            font-size: 12px;
            font-weight: bold;
        """)

    def set_status(self, status: str, text: str = None):
        """Update badge status and optionally text."""
        self._status = status
        if text:
            self.setText(text)
        self._apply_style()


class WorkStatusCard(QGroupBox):
    """Display work status with timing information."""

    def __init__(self):
        super().__init__("작업 상태")
        self.setObjectName("work_status_card")

        self._start_time = None
        self._is_working = False

        # Timer for elapsed time
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_elapsed)

        self.setup_ui()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(8, 8, 8, 8)

        # LOT number (prominent display)
        lot_row = QHBoxLayout()
        lot_label = QLabel("LOT:")
        self.lot_value = QLabel("대기중")
        self.lot_value.setObjectName("lot_number")
        lot_row.addWidget(lot_label)
        lot_row.addStretch()
        lot_row.addWidget(self.lot_value)
        layout.addLayout(lot_row)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #1a1a1a;")
        layout.addWidget(separator)

        # Start status row (착공)
        start_row = QHBoxLayout()
        start_label = QLabel("착공:")
        self.start_badge = StatusBadge("대기", "default")
        self.start_time_value = QLabel("-")
        self.start_time_value.setObjectName("info_value")
        start_row.addWidget(start_label)
        start_row.addWidget(self.start_badge)
        start_row.addStretch()
        start_row.addWidget(self.start_time_value)
        layout.addLayout(start_row)

        # Complete status row (완공)
        complete_row = QHBoxLayout()
        complete_label = QLabel("완공:")
        self.complete_badge = StatusBadge("미완료", "default")
        self.complete_time_value = QLabel("-")
        self.complete_time_value.setObjectName("info_value")
        complete_row.addWidget(complete_label)
        complete_row.addWidget(self.complete_badge)
        complete_row.addStretch()
        complete_row.addWidget(self.complete_time_value)
        layout.addLayout(complete_row)

        # Elapsed time row (진행)
        elapsed_row = QHBoxLayout()
        elapsed_label = QLabel("진행:")
        self.elapsed_value = QLabel("00:00:00")
        self.elapsed_value.setObjectName("elapsed_time")
        elapsed_row.addWidget(elapsed_label)
        elapsed_row.addStretch()
        elapsed_row.addWidget(self.elapsed_value)
        layout.addLayout(elapsed_row)

    def _update_elapsed(self):
        """Update elapsed time display."""
        if self._start_time and self._is_working:
            elapsed = datetime.now() - self._start_time
            hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.elapsed_value.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    def update_time(self, time_str: str):
        """Update elapsed time display from external source."""
        self.elapsed_value.setText(time_str)

    def set_lot(self, lot_number: str):
        """Set LOT number."""
        self.lot_value.setText(lot_number if lot_number else "대기중")

    def start_work(self, lot_number: str, start_time: str):
        """Mark work as started."""
        self.set_lot(lot_number)
        self._start_time = datetime.now()
        self._is_working = True

        self.start_badge.set_status("active", "작업중")
        self.start_time_value.setText(start_time)
        self.complete_badge.set_status("default", "미완료")
        self.complete_time_value.setText("-")

        # Start elapsed timer
        self._timer.start(1000)
        logger.debug(f"Work started: {lot_number}")

    def complete_work(self, complete_time: str):
        """Mark work as completed."""
        self._is_working = False
        self._timer.stop()

        self.start_badge.set_status("success", "완료")  # 착공도 완료 상태로 변경
        self.complete_badge.set_status("success", "완료")
        self.complete_time_value.setText(complete_time)
        logger.debug("Work completed")

    def reset(self):
        """Reset to initial state."""
        self._start_time = None
        self._is_working = False
        self._timer.stop()

        self.lot_value.setText("대기중")
        self.start_badge.set_status("default", "대기")
        self.start_time_value.setText("-")
        self.elapsed_value.setText("00:00:00")
        self.complete_badge.set_status("default", "미완료")
        self.complete_time_value.setText("-")

    def is_working(self) -> bool:
        """Check if work is currently in progress."""
        return self._is_working

    def cleanup(self):
        """Stop timer for cleanup."""
        self._timer.stop()
