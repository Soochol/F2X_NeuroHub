"""
Process Info Card Widget - Displays process, worker, line information.
"""
import logging
from typing import Any

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout

from utils.theme_manager import get_theme

logger = logging.getLogger(__name__)
theme = get_theme()


class ProcessInfoCard(QGroupBox):
    """Display process information from configuration."""

    def __init__(self, config: Any) -> None:
        super().__init__("공정 정보")
        self.config = config
        self.setObjectName("process_info_card")
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        # Process name row
        process_row = QHBoxLayout()
        process_label = QLabel("공정:")
        self.process_value = QLabel(self.config.process_name)
        self.process_value.setObjectName("info_value")
        process_row.addWidget(process_label)
        process_row.addStretch()
        process_row.addWidget(self.process_value)
        layout.addLayout(process_row)

        # Worker row
        worker_row = QHBoxLayout()
        worker_label = QLabel("작업자:")
        self.worker_value = QLabel("-")
        self.worker_value.setObjectName("info_value")
        worker_row.addWidget(worker_label)
        worker_row.addStretch()
        worker_row.addWidget(self.worker_value)
        layout.addLayout(worker_row)

        # Line row
        line_row = QHBoxLayout()
        line_label = QLabel("라인:")
        self.line_value = QLabel(self.config.line_id)
        self.line_value.setObjectName("info_value")
        line_row.addWidget(line_label)
        line_row.addStretch()
        line_row.addWidget(self.line_value)
        layout.addLayout(line_row)

        # Equipment row
        equip_row = QHBoxLayout()
        equip_label = QLabel("설비:")
        self.equip_value = QLabel(self.config.equipment_id)
        self.equip_value.setObjectName("info_value")
        equip_row.addWidget(equip_label)
        equip_row.addStretch()
        equip_row.addWidget(self.equip_value)
        layout.addLayout(equip_row)

    def set_worker(self, worker_id: str) -> None:
        """Update worker ID."""
        self.worker_value.setText(worker_id if worker_id else "-")

    def update_from_config(self) -> None:
        """Update all values from config."""
        self.process_value.setText(self.config.process_name)
        self.line_value.setText(self.config.line_id)
        self.equip_value.setText(self.config.equipment_id)