"""
Home Page - Work status display.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PySide6.QtCore import Qt
from widgets.work_status_card import WorkStatusCard
from widgets.base_components import ThemedLabel


class HomePage(QWidget):
    """Home page showing current work status."""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setup_ui()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Header
        header = QLabel("작업 현황")
        header.setStyleSheet("font-size: 16px; font-weight: 600; color: #ededed; margin-bottom: 8px;")
        layout.addWidget(header)

        desc = QLabel("현재 작업 상태를 확인합니다.")
        desc.setStyleSheet("color: #9ca3af; font-size: 12px; margin-bottom: 16px;")
        layout.addWidget(desc)

        # Process info section
        process_group = QFrame()
        process_group.setObjectName("process_info_frame")
        process_group.setStyleSheet("""
            #process_info_frame {
                background-color: #0a0a0a;
                border: 1px solid #1a1a1a;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        process_layout = QVBoxLayout(process_group)
        process_layout.setContentsMargins(16, 16, 16, 16)
        process_layout.setSpacing(8)

        # Process name
        process_name_layout = QHBoxLayout()
        process_name_label = QLabel("공정:")
        process_name_label.setStyleSheet("color: #9ca3af; font-size: 13px;")
        self.process_name_value = QLabel(self.config.process_name)
        self.process_name_value.setStyleSheet("color: #3ECF8E; font-size: 13px; font-weight: 600;")
        process_name_layout.addWidget(process_name_label)
        process_name_layout.addWidget(self.process_name_value)
        process_name_layout.addStretch()
        process_layout.addLayout(process_name_layout)

        # Line info
        line_layout = QHBoxLayout()
        line_label = QLabel("라인:")
        line_label.setStyleSheet("color: #9ca3af; font-size: 13px;")
        self.line_value = QLabel(self.config.line_id)
        self.line_value.setStyleSheet("color: #ededed; font-size: 13px;")
        line_layout.addWidget(line_label)
        line_layout.addWidget(self.line_value)
        line_layout.addStretch()
        process_layout.addLayout(line_layout)

        # Equipment info
        equip_layout = QHBoxLayout()
        equip_label = QLabel("장비:")
        equip_label.setStyleSheet("color: #9ca3af; font-size: 13px;")
        self.equip_value = QLabel(self.config.equipment_id)
        self.equip_value.setStyleSheet("color: #ededed; font-size: 13px;")
        equip_layout.addWidget(equip_label)
        equip_layout.addWidget(self.equip_value)
        equip_layout.addStretch()
        process_layout.addLayout(equip_layout)

        layout.addWidget(process_group)

        # Work status card
        self.work_card = WorkStatusCard()
        layout.addWidget(self.work_card)

        # Status message
        self.status_label = QLabel("바코드 스캔 대기중...")
        self.status_label.setObjectName("status_label")
        self.status_label.setStyleSheet("color: #9ca3af; font-size: 13px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Recent completion label
        self.recent_label = QLabel("")
        self.recent_label.setObjectName("recent_label")
        self.recent_label.setStyleSheet("color: #6b7280; font-size: 12px;")
        self.recent_label.setAlignment(Qt.AlignCenter)
        self.recent_label.setWordWrap(True)
        layout.addWidget(self.recent_label)

        layout.addStretch()

    def set_status(self, message: str, variant: str = "default"):
        """Set status message with optional styling."""
        self.status_label.setText(message)

        color_map = {
            "default": "#9ca3af",
            "success": "#3ECF8E",
            "danger": "#ef4444",
            "warning": "#f59e0b"
        }
        color = color_map.get(variant, "#9ca3af")
        self.status_label.setStyleSheet(f"color: {color}; font-size: 13px;")

    def set_recent_message(self, message: str):
        """Set recent completion message."""
        self.recent_label.setText(message)

    def start_work(self, lot_number: str, start_time: str):
        """Update UI for work started."""
        self.work_card.start_work(lot_number, start_time)
        self.set_status(f"착공 완료: {lot_number}", "success")

    def complete_work(self, complete_time: str):
        """Update UI for work completed."""
        self.work_card.complete_work(complete_time)

    def reset(self):
        """Reset work status."""
        self.work_card.reset()
        self.set_status("바코드 스캔 대기중...", "default")
        self.recent_label.setText("")

    def cleanup(self):
        """Cleanup resources."""
        self.work_card.cleanup()
