"""
Complete Work Page - PASS/FAIL completion buttons.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                                QFrame, QHBoxLayout)
from PySide6.QtCore import Signal
from utils.theme_manager import get_theme
from utils.serial_validator import format_serial_number_v1

theme = get_theme()


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

        # Theme colors
        text_primary = theme.get('colors.text.primary')
        text_on_dark = theme.get('colors.text.onDark')
        grey_300 = theme.get('colors.grey.300')
        grey_400 = theme.get('colors.grey.400')
        grey_600 = theme.get('colors.grey.600')
        bg_default = theme.get('colors.background.default')
        border_default = theme.get('colors.border.default')
        border_light = theme.get('colors.border.light')
        brand = theme.get('colors.brand.main')
        success_main = theme.get('colors.success.main')
        success_dark = theme.get('colors.success.dark')
        danger_main = theme.get('colors.danger.main')
        danger_dark = theme.get('colors.danger.dark')

        # Header
        header = QLabel("완공")
        header.setStyleSheet(
            f"font-size: 16px; font-weight: 600; color: {text_primary}; margin-bottom: 8px;"
        )
        layout.addWidget(header)

        desc = QLabel("작업 결과를 선택하여 완공 처리합니다.")
        desc.setStyleSheet(f"color: {grey_400}; font-size: 12px; margin-bottom: 16px;")
        layout.addWidget(desc)

        # Current work info
        self.work_info_frame = QFrame()
        self.work_info_frame.setObjectName("work_info_frame")
        self.work_info_frame.setStyleSheet(f"""
            #work_info_frame {{
                background-color: {bg_default};
                border: 1px solid {border_default};
                border-radius: 8px;
            }}
        """)
        work_info_layout = QVBoxLayout(self.work_info_frame)
        work_info_layout.setContentsMargins(16, 16, 16, 16)
        work_info_layout.setSpacing(8)

        work_title = QLabel("현재 작업")
        work_title.setStyleSheet(f"color: {grey_300}; font-size: 13px; font-weight: 600;")
        work_info_layout.addWidget(work_title)

        # LOT number display
        lot_layout = QHBoxLayout()
        lot_label = QLabel("LOT:")
        lot_label.setStyleSheet(f"color: {grey_400}; font-size: 13px;")
        self.lot_value = QLabel("-")
        self.lot_value.setStyleSheet(f"color: {brand}; font-size: 13px; font-weight: 600;")
        lot_layout.addWidget(lot_label)
        lot_layout.addWidget(self.lot_value)
        lot_layout.addStretch()
        work_info_layout.addLayout(lot_layout)

        # Serial number display (conditional - only shown for serial-level work)
        serial_layout = QHBoxLayout()
        serial_label = QLabel("Serial:")
        serial_label.setStyleSheet(f"color: {grey_400}; font-size: 13px;")
        self.serial_value = QLabel("-")
        self.serial_value.setStyleSheet(f"color: {brand}; font-size: 13px; font-weight: 600;")
        serial_layout.addWidget(serial_label)
        serial_layout.addWidget(self.serial_value)
        serial_layout.addStretch()
        self.serial_layout_container = serial_layout
        self.serial_label_widget = serial_label
        self.serial_value_widget = self.serial_value
        work_info_layout.addLayout(serial_layout)
        # Hide serial row by default
        serial_label.hide()
        self.serial_value.hide()

        # Elapsed time display
        time_layout = QHBoxLayout()
        time_label = QLabel("경과 시간:")
        time_label.setStyleSheet(f"color: {grey_400}; font-size: 13px;")
        self.time_value = QLabel("-")
        self.time_value.setStyleSheet(f"color: {text_primary}; font-size: 13px;")
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_value)
        time_layout.addStretch()
        work_info_layout.addLayout(time_layout)

        # Process display
        process_layout = QHBoxLayout()
        process_label = QLabel("공정:")
        process_label.setStyleSheet(f"color: {grey_400}; font-size: 13px;")
        self.process_value = QLabel(self._get_process_display())
        self.process_value.setStyleSheet(f"color: {text_primary}; font-size: 13px;")
        process_layout.addWidget(process_label)
        process_layout.addWidget(self.process_value)
        process_layout.addStretch()
        work_info_layout.addLayout(process_layout)

        # Production line display
        line_layout = QHBoxLayout()
        line_label = QLabel("생산라인:")
        line_label.setStyleSheet(f"color: {grey_400}; font-size: 13px;")
        self.line_value = QLabel(self._get_line_display())
        self.line_value.setStyleSheet(f"color: {text_primary}; font-size: 13px;")
        line_layout.addWidget(line_label)
        line_layout.addWidget(self.line_value)
        line_layout.addStretch()
        work_info_layout.addLayout(line_layout)

        # Equipment display
        equip_layout_row = QHBoxLayout()
        equip_label = QLabel("장비:")
        equip_label.setStyleSheet(f"color: {grey_400}; font-size: 13px;")
        self.equip_value = QLabel(self._get_equipment_display())
        self.equip_value.setStyleSheet(f"color: {text_primary}; font-size: 13px;")
        equip_layout_row.addWidget(equip_label)
        equip_layout_row.addWidget(self.equip_value)
        equip_layout_row.addStretch()
        work_info_layout.addLayout(equip_layout_row)

        layout.addWidget(self.work_info_frame)

        # Completion buttons section
        button_group = QFrame()
        button_group.setObjectName("button_group_frame")
        button_group.setStyleSheet(f"""
            #button_group_frame {{
                background-color: {bg_default};
                border: 1px solid {border_default};
                border-radius: 8px;
            }}
        """)
        button_layout = QVBoxLayout(button_group)
        button_layout.setContentsMargins(16, 16, 16, 16)
        button_layout.setSpacing(12)

        button_title = QLabel("작업 결과")
        button_title.setStyleSheet(f"color: {grey_300}; font-size: 13px; font-weight: 600;")
        button_layout.addWidget(button_title)

        # PASS/FAIL buttons row
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(12)

        # PASS button
        self.pass_button = QPushButton("PASS 완공")
        self.pass_button.setObjectName("pass_button")
        self.pass_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {success_main};
                border: none;
                border-radius: 6px;
                padding: 16px 24px;
                color: {text_on_dark};
                font-size: 14px;
                font-weight: 600;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: {success_dark};
            }}
            QPushButton:disabled {{
                background-color: {border_light};
                color: {grey_600};
            }}
        """)
        self.pass_button.clicked.connect(self._on_pass_clicked)
        self.pass_button.setEnabled(False)
        buttons_row.addWidget(self.pass_button)

        # FAIL button
        self.fail_button = QPushButton("FAIL 완공")
        self.fail_button.setObjectName("fail_button")
        self.fail_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {danger_main};
                border: none;
                border-radius: 6px;
                padding: 16px 24px;
                color: {text_on_dark};
                font-size: 14px;
                font-weight: 600;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: {danger_dark};
            }}
            QPushButton:disabled {{
                background-color: {border_light};
                color: {grey_600};
            }}
        """)
        self.fail_button.clicked.connect(self._on_fail_clicked)
        self.fail_button.setEnabled(False)
        buttons_row.addWidget(self.fail_button)

        button_layout.addLayout(buttons_row)
        layout.addWidget(button_group)

        # Info section
        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_default};
                border: 1px solid {border_default};
                border-radius: 8px;
            }}
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(16, 16, 16, 16)
        info_layout.setSpacing(8)

        info_title = QLabel("안내")
        info_title.setStyleSheet(f"color: {grey_300}; font-size: 13px; font-weight: 600;")
        info_layout.addWidget(info_title)

        info_text = QLabel(
            "• 작업이 정상 완료되면 'PASS 완공' 버튼을 클릭합니다.\n"
            "• 불량이 발생한 경우 'FAIL 완공' 버튼을 클릭하고\n"
            "  불량 유형을 선택합니다.\n"
            "• 착공 후에만 완공 버튼이 활성화됩니다."
        )
        info_text.setStyleSheet(f"color: {grey_400}; font-size: 12px; line-height: 1.5;")
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

    def set_work_info(self, lot_number: str, elapsed_time: str = "-", serial_number: str = None):
        """Set current work information."""
        self.lot_value.setText(lot_number if lot_number else "-")
        self.time_value.setText(elapsed_time)

        # Show/hide serial number
        if serial_number:
            formatted_serial = format_serial_number_v1(serial_number)
            self.serial_value.setText(formatted_serial)
            self.serial_label_widget.show()
            self.serial_value_widget.show()
        else:
            self.serial_value.setText("-")
            self.serial_label_widget.hide()
            self.serial_value_widget.hide()

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
        self.serial_value.setText("-")
        self.serial_label_widget.hide()
        self.serial_value_widget.hide()
        self.time_value.setText("-")
        self.set_enabled(False)

    def _get_process_display(self) -> str:
        """Get process display text from config."""
        number = self.config.process_number
        name = self.config.process_name
        if number and name:
            return f"{number}. {name}"
        elif number:
            return f"Process {number}"
        return "(미설정)"

    def _get_line_display(self) -> str:
        """Get production line display text from config."""
        code = self.config.line_code
        name = self.config.line_name
        if code and name:
            return f"{code} - {name}"
        elif code:
            return code
        return "(미설정)"

    def _get_equipment_display(self) -> str:
        """Get equipment display text from config."""
        code = self.config.equipment_code
        name = self.config.equipment_name
        if code and name:
            return f"{code} - {name}"
        elif code:
            return code
        return "(미설정)"

    def refresh_info(self):
        """Refresh displayed process/equipment/line info from config."""
        self.process_value.setText(self._get_process_display())
        self.line_value.setText(self._get_line_display())
        self.equip_value.setText(self._get_equipment_display())
