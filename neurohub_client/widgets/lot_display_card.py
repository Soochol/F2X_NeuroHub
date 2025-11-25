"""
LOT Display Card Widget - QGroupBox style card panel.
"""
import logging

from PySide6.QtWidgets import QVBoxLayout, QLabel, QGroupBox
from PySide6.QtCore import Qt
from utils.theme_manager import get_theme

logger = logging.getLogger(__name__)
theme = get_theme()


class LotDisplayCard(QGroupBox):
    """Display current LOT information with process name as card title."""

    def __init__(self, process_name: str = ""):
        title = f"공정: {process_name}" if process_name else "현재 작업"
        super().__init__(title)
        self.process_name = process_name
        self.setObjectName("lot_display_card")
        self.setup_ui()
        self._apply_theme()

    def _apply_theme(self):
        """Apply theme styling to card (QGroupBox style)."""
        if not theme:
            return

        bg_default = theme.get("colors.background.default", "#0f0f0f")
        bg_elevated = theme.get("colors.background.elevated", "#1f1f1f")
        text_primary = theme.get("colors.text.primary", "#ededed")
        text_secondary = theme.get("colors.text.secondary", "#a8a8a8")
        border_default = theme.get("colors.border.default", "#1a1a1a")
        brand_main = theme.get("colors.brand.main", "#3ECF8E")
        radius_md = theme.get("radius.md", 8)
        radius_lg = theme.get("radius.lg", 16)

        self.setStyleSheet(f"""
            QGroupBox#lot_display_card {{
                background-color: {bg_default};
                border: 1px solid {border_default};
                border-radius: {radius_lg}px;
                margin-top: 16px;
                padding: 16px;
                padding-top: 28px;
                font-weight: bold;
                color: {text_primary};
            }}

            QGroupBox#lot_display_card::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
                background-color: {bg_elevated};
                border-radius: {radius_md}px;
                color: {brand_main};
            }}

            QLabel {{
                color: {text_secondary};
                background-color: transparent;
            }}
        """)

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 8, 8, 8)

        # LOT number (main display)
        self.lot_label = QLabel("LOT: 대기중")
        self.lot_label.setObjectName("lot_number")
        self.lot_label.setAlignment(Qt.AlignCenter)
        self.lot_label.setWordWrap(True)
        if theme:
            lot_size = 24
            brand = theme.get("colors.brand.main", "#3ECF8E")
            bg_soft = theme.get("colors.glow.brandSoft", "#3ECF8E40")
            radius = theme.get("radius.md", 8)
            self.lot_label.setStyleSheet(f"""
                font-size: {lot_size}px;
                font-weight: bold;
                color: {brand};
                background-color: {bg_soft};
                border-radius: {radius}px;
                padding: 12px;
                margin: 8px 0;
            """)
        layout.addWidget(self.lot_label)

        # Info section (worker and time)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)

        # Worker
        self.worker_label = QLabel("작업자: -")
        self.worker_label.setObjectName("worker_label")
        if theme:
            secondary = theme.get("colors.text.secondary", "#a8a8a8")
            body_size = theme.get("typography.size.body", 14)
            self.worker_label.setStyleSheet(f"""
                font-size: {body_size}px;
                color: {secondary};
                padding: 4px 0;
            """)
        info_layout.addWidget(self.worker_label)

        # Start time
        self.time_label = QLabel("시작: -")
        self.time_label.setObjectName("time_label")
        if theme:
            secondary = theme.get("colors.text.secondary", "#a8a8a8")
            body_size = theme.get("typography.size.body", 14)
            self.time_label.setStyleSheet(f"""
                font-size: {body_size}px;
                color: {secondary};
                padding: 4px 0;
            """)
        info_layout.addWidget(self.time_label)

        layout.addLayout(info_layout)

    def set_process_name(self, name: str):
        """Update process name in title."""
        self.process_name = name
        self.setTitle(f"공정: {name}")

    def update_lot(self, lot_number: str, worker_id: str, start_time: str):
        """Update LOT information."""
        self.lot_label.setText(f"LOT: {lot_number}")
        self.worker_label.setText(f"작업자: {worker_id}")
        self.time_label.setText(f"시작: {start_time}")
        logger.debug("LOT card updated: %s", lot_number)

    def clear(self):
        """Clear LOT information."""
        self.lot_label.setText("LOT: 대기중")
        self.worker_label.setText("작업자: -")
        self.time_label.setText("시작: -")
        logger.debug("LOT card cleared")
