"""
Complete Work Page - PASS/FAIL completion buttons.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                                QFrame, QHBoxLayout)
from PySide6.QtCore import Signal


class CompleteWorkPage(QWidget):
    """Complete work page with PASS/FAIL buttons."""

    # Signals
    pass_requested = Signal()
    fail_requested = Signal()

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
        header = QLabel("완공")
        header.setStyleSheet("font-size: 16px; font-weight: 600; color: #ededed; margin-bottom: 8px;")
        layout.addWidget(header)

        desc = QLabel("작업 결과를 선택하여 완공 처리합니다.")
        desc.setStyleSheet("color: #9ca3af; font-size: 12px; margin-bottom: 16px;")
        layout.addWidget(desc)

        # Current work info
        self.work_info_frame = QFrame()
        self.work_info_frame.setObjectName("work_info_frame")
        self.work_info_frame.setStyleSheet("""
            #work_info_frame {
                background-color: #0a0a0a;
                border: 1px solid #1a1a1a;
                border-radius: 8px;
            }
        """)
        work_info_layout = QVBoxLayout(self.work_info_frame)
        work_info_layout.setContentsMargins(16, 16, 16, 16)
        work_info_layout.setSpacing(8)

        work_title = QLabel("현재 작업")
        work_title.setStyleSheet("color: #d1d5db; font-size: 13px; font-weight: 600;")
        work_info_layout.addWidget(work_title)

        # LOT number display
        lot_layout = QHBoxLayout()
        lot_label = QLabel("LOT:")
        lot_label.setStyleSheet("color: #9ca3af; font-size: 13px;")
        self.lot_value = QLabel("-")
        self.lot_value.setStyleSheet("color: #3ECF8E; font-size: 13px; font-weight: 600;")
        lot_layout.addWidget(lot_label)
        lot_layout.addWidget(self.lot_value)
        lot_layout.addStretch()
        work_info_layout.addLayout(lot_layout)

        # Elapsed time display
        time_layout = QHBoxLayout()
        time_label = QLabel("경과 시간:")
        time_label.setStyleSheet("color: #9ca3af; font-size: 13px;")
        self.time_value = QLabel("-")
        self.time_value.setStyleSheet("color: #ededed; font-size: 13px;")
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_value)
        time_layout.addStretch()
        work_info_layout.addLayout(time_layout)

        layout.addWidget(self.work_info_frame)

        # Completion buttons section
        button_group = QFrame()
        button_group.setObjectName("button_group_frame")
        button_group.setStyleSheet("""
            #button_group_frame {
                background-color: #0a0a0a;
                border: 1px solid #1a1a1a;
                border-radius: 8px;
            }
        """)
        button_layout = QVBoxLayout(button_group)
        button_layout.setContentsMargins(16, 16, 16, 16)
        button_layout.setSpacing(12)

        button_title = QLabel("작업 결과")
        button_title.setStyleSheet("color: #d1d5db; font-size: 13px; font-weight: 600;")
        button_layout.addWidget(button_title)

        # PASS/FAIL buttons row
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(12)

        # PASS button
        self.pass_button = QPushButton("PASS 완공")
        self.pass_button.setObjectName("pass_button")
        self.pass_button.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                border: none;
                border-radius: 6px;
                padding: 16px 24px;
                color: #ffffff;
                font-size: 14px;
                font-weight: 600;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #6b7280;
            }
        """)
        self.pass_button.clicked.connect(self._on_pass_clicked)
        self.pass_button.setEnabled(False)
        buttons_row.addWidget(self.pass_button)

        # FAIL button
        self.fail_button = QPushButton("FAIL 완공")
        self.fail_button.setObjectName("fail_button")
        self.fail_button.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                border: none;
                border-radius: 6px;
                padding: 16px 24px;
                color: #ffffff;
                font-size: 14px;
                font-weight: 600;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #6b7280;
            }
        """)
        self.fail_button.clicked.connect(self._on_fail_clicked)
        self.fail_button.setEnabled(False)
        buttons_row.addWidget(self.fail_button)

        button_layout.addLayout(buttons_row)
        layout.addWidget(button_group)

        # Info section
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #0a0a0a;
                border: 1px solid #1a1a1a;
                border-radius: 8px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(16, 16, 16, 16)
        info_layout.setSpacing(8)

        info_title = QLabel("안내")
        info_title.setStyleSheet("color: #d1d5db; font-size: 13px; font-weight: 600;")
        info_layout.addWidget(info_title)

        info_text = QLabel(
            "• 작업이 정상 완료되면 'PASS 완공' 버튼을 클릭합니다.\n"
            "• 불량이 발생한 경우 'FAIL 완공' 버튼을 클릭하고\n"
            "  불량 유형을 선택합니다.\n"
            "• 착공 후에만 완공 버튼이 활성화됩니다."
        )
        info_text.setStyleSheet("color: #9ca3af; font-size: 12px; line-height: 1.5;")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)

        layout.addWidget(info_frame)

        layout.addStretch()

    def _on_pass_clicked(self):
        """Handle PASS button click."""
        self.pass_requested.emit()

    def _on_fail_clicked(self):
        """Handle FAIL button click."""
        self.fail_requested.emit()

    def set_work_info(self, lot_number: str, elapsed_time: str = "-"):
        """Set current work information."""
        self.lot_value.setText(lot_number if lot_number else "-")
        self.time_value.setText(elapsed_time)

    def update_elapsed_time(self, elapsed_time: str):
        """Update elapsed time display."""
        self.time_value.setText(elapsed_time)

    def set_enabled(self, enabled: bool):
        """Enable or disable the completion buttons."""
        self.pass_button.setEnabled(enabled)
        self.fail_button.setEnabled(enabled)

    def reset(self):
        """Reset to initial state."""
        self.lot_value.setText("-")
        self.time_value.setText("-")
        self.set_enabled(False)
