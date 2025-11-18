"""
LOT Display Card Widget.
"""
from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from widgets.base_components import InfoCard, ThemedLabel
from utils.theme_manager import get_theme
import logging

logger = logging.getLogger(__name__)
theme = get_theme()


class LotDisplayCard(InfoCard):
    """Display current LOT information."""

    def __init__(self):
        super().__init__(title="현재 LOT 정보", min_height=120)
        self.setup_ui()

    def setup_ui(self):
        """Setup UI components."""
        # LOT number (larger, more prominent)
        lot_style = theme.get_component_style('lotCard.lotLabel')
        self.lot_label = QLabel("LOT: 대기중")
        self.lot_label.setStyleSheet(theme.build_stylesheet(lot_style))
        self.lot_label.setWordWrap(True)
        self.content_layout.addWidget(self.lot_label)

        # Worker
        self.worker_label = ThemedLabel("작업자: -", style_type="secondary")
        self.content_layout.addWidget(self.worker_label)

        # Start time
        self.time_label = ThemedLabel("시작: -", style_type="secondary")
        self.content_layout.addWidget(self.time_label)

    def update_lot(self, lot_number: str, worker_id: str, start_time: str):
        """
        Update LOT information.

        Args:
            lot_number: LOT number
            worker_id: Worker ID
            start_time: Start time (HH:MM:SS)
        """
        self.lot_label.setText(f"LOT: {lot_number}")
        self.worker_label.setText(f"작업자: {worker_id}")
        self.time_label.setText(f"시작: {start_time}")
        logger.debug(f"LOT card updated: {lot_number}")

    def clear(self):
        """Clear LOT information."""
        self.lot_label.setText("LOT: 대기중")
        self.worker_label.setText("작업자: -")
        self.time_label.setText("시작: -")
        logger.debug("LOT card cleared")
