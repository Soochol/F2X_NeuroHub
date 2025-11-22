"""
Start Work Page - LOT input and start button.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                                QPushButton, QFrame, QHBoxLayout)
from PySide6.QtCore import Qt, Signal
from utils.theme_manager import get_theme
from utils.serial_validator import validate_serial_number_v1, format_serial_number_v1

theme = get_theme()


class StartWorkPage(QWidget):
    """Start work page with LOT input and start button."""

    # Signals
    start_requested = Signal(str)  # lot_number
    serial_start_requested = Signal(str, str)  # lot_number, serial_number

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
        grey_300 = theme.get('colors.grey.300')
        grey_400 = theme.get('colors.grey.400')
        grey_600 = theme.get('colors.grey.600')
        bg_default = theme.get('colors.background.default')
        bg_elevated = theme.get('colors.background.elevated')
        border_default = theme.get('colors.border.default')
        border_light = theme.get('colors.border.light')
        brand = theme.get('colors.brand.main')
        brand_light = theme.get('colors.brand.light')
        text_on_brand = theme.get('colors.text.onBrand')
        danger_main = theme.get('colors.danger.main')

        # Header
        header = QLabel("착공")
        header.setStyleSheet(
            f"font-size: 16px; font-weight: 600; color: {text_primary}; margin-bottom: 8px;"
        )
        layout.addWidget(header)

        desc = QLabel("LOT 바코드를 스캔하거나 입력하여 착공합니다.")
        desc.setStyleSheet(f"color: {grey_400}; font-size: 12px; margin-bottom: 16px;")
        layout.addWidget(desc)

        # LOT input section
        input_group = QFrame()
        input_group.setObjectName("lot_input_frame")
        input_group.setStyleSheet(f"""
            #lot_input_frame {{
                background-color: {bg_default};
                border: 1px solid {border_default};
                border-radius: 8px;
            }}
        """)
        input_layout = QVBoxLayout(input_group)
        input_layout.setContentsMargins(16, 16, 16, 16)
        input_layout.setSpacing(12)

        # LOT input label
        lot_label = QLabel("WIP ID / LOT 번호")
        lot_label.setStyleSheet(f"color: {grey_300}; font-size: 13px; font-weight: 500;")
        input_layout.addWidget(lot_label)

        # LOT input field
        self.lot_input = QLineEdit()
        self.lot_input.setObjectName("lot_input")
        self.lot_input.setPlaceholderText("LOT 바코드를 스캔하세요...")
        self.lot_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {bg_elevated};
                border: 1px solid {border_light};
                border-radius: 6px;
                padding: 12px 16px;
                color: {text_primary};
                font-size: 14px;
                min-height: 24px;
            }}
            QLineEdit:focus {{
                border-color: {brand};
            }}
        """)
        self.lot_input.returnPressed.connect(self._on_start_clicked)
        input_layout.addWidget(self.lot_input)

        # Serial input (Process 7 only)
        self.serial_label = QLabel("Serial 번호 (선택사항)")
        self.serial_label.setStyleSheet(f"color: {grey_300}; font-size: 13px; font-weight: 500; margin-top: 8px;")
        input_layout.addWidget(self.serial_label)

        self.serial_input = QLineEdit()
        self.serial_input.setObjectName("serial_input")
        self.serial_input.setPlaceholderText("Serial 바코드를 스캔하세요... (선택)")
        self.serial_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {bg_elevated};
                border: 1px solid {border_light};
                border-radius: 6px;
                padding: 12px 16px;
                color: {text_primary};
                font-size: 14px;
                min-height: 24px;
            }}
            QLineEdit:focus {{
                border-color: {brand};
            }}
            QLineEdit[invalid="true"] {{
                border-color: {danger_main};
            }}
        """)
        self.serial_input.returnPressed.connect(self._on_start_clicked)
        self.serial_input.textChanged.connect(self._on_serial_changed)
        input_layout.addWidget(self.serial_input)

        # Validation message label
        self.serial_validation_label = QLabel("")
        self.serial_validation_label.setStyleSheet(f"color: {danger_main}; font-size: 11px;")
        self.serial_validation_label.hide()
        input_layout.addWidget(self.serial_validation_label)

        # Hide serial input by default (show only for Process 7)
        self._set_serial_input_visible(self.config.process_number == 7)

        # Start button
        self.start_button = QPushButton("착공 시작")
        self.start_button.setObjectName("start_button")
        self.start_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {brand};
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                color: {text_on_brand};
                font-size: 14px;
                font-weight: 600;
                min-height: 24px;
            }}
            QPushButton:hover {{
                background-color: {brand_light};
            }}
            QPushButton:disabled {{
                background-color: {border_light};
                color: {grey_600};
            }}
        """)
        self.start_button.clicked.connect(self._on_start_clicked)
        input_layout.addWidget(self.start_button)

        layout.addWidget(input_group)

        # Current equipment info section
        equip_frame = QFrame()
        equip_frame.setObjectName("equip_info_frame")
        equip_frame.setStyleSheet(f"""
            #equip_info_frame {{
                background-color: {bg_default};
                border: 1px solid {border_default};
                border-radius: 8px;
            }}
        """)
        equip_layout = QVBoxLayout(equip_frame)
        equip_layout.setContentsMargins(16, 12, 16, 12)
        equip_layout.setSpacing(8)

        equip_title = QLabel("현재 설정")
        equip_title.setStyleSheet(f"color: {grey_300}; font-size: 13px; font-weight: 600;")
        equip_layout.addWidget(equip_title)

        # Process info
        process_text = self._get_process_display()
        self.process_info_label = QLabel(f"공정: {process_text}")
        self.process_info_label.setStyleSheet(f"color: {grey_400}; font-size: 12px;")
        equip_layout.addWidget(self.process_info_label)

        # Line info
        line_text = self._get_line_display()
        self.line_info_label = QLabel(f"생산라인: {line_text}")
        self.line_info_label.setStyleSheet(f"color: {grey_400}; font-size: 12px;")
        equip_layout.addWidget(self.line_info_label)

        # Equipment info
        equip_text = self._get_equipment_display()
        self.equip_info_label = QLabel(f"장비: {equip_text}")
        self.equip_info_label.setStyleSheet(f"color: {grey_400}; font-size: 12px;")
        equip_layout.addWidget(self.equip_info_label)

        layout.addWidget(equip_frame)

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
            "• 바코드 스캐너로 LOT 바코드를 스캔하면 자동 입력됩니다.\n"
            "• Enter 키를 누르거나 '착공 시작' 버튼을 클릭하여 착공합니다.\n"
            "• 착공 후에는 완공 메뉴에서 작업을 완료할 수 있습니다."
        )
        info_text.setStyleSheet(f"color: {grey_400}; font-size: 12px; line-height: 1.5;")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)

        layout.addWidget(info_frame)

        layout.addStretch()

    def _on_start_clicked(self):
        """Handle start button click."""
        lot_number = self.lot_input.text().strip()
        serial_number = self.serial_input.text().strip()

        if not lot_number:
            return

        # Validate serial if provided
        if serial_number:
            if not validate_serial_number_v1(serial_number):
                self.serial_validation_label.setText("❌ 잘못된 Serial 번호 형식입니다 (14자: KR01PSA2511001)")
                self.serial_validation_label.show()
                self.serial_input.setProperty("invalid", "true")
                self.serial_input.style().unpolish(self.serial_input)
                self.serial_input.style().polish(self.serial_input)
                return
            # Valid serial - emit with serial
            self.serial_start_requested.emit(lot_number, serial_number)
        else:
            # No serial - LOT-level work
            self.start_requested.emit(lot_number)

    def _on_serial_changed(self, text: str):
        """Handle serial input text change - clear validation error."""
        if text:
            # Clear validation error when user types
            self.serial_validation_label.hide()
            self.serial_input.setProperty("invalid", "false")
            self.serial_input.style().unpolish(self.serial_input)
            self.serial_input.style().polish(self.serial_input)

    def set_lot_number(self, lot_number: str):
        """Set LOT number in input field."""
        self.lot_input.setText(lot_number)

    def set_serial_number(self, serial_number: str):
        """Set Serial number in input field."""
        self.serial_input.setText(serial_number)

    def clear_input(self):
        """Clear input fields."""
        self.lot_input.clear()
        self.serial_input.clear()
        self.serial_validation_label.hide()

    def set_enabled(self, enabled: bool):
        """Enable or disable the start controls."""
        self.lot_input.setEnabled(enabled)
        self.serial_input.setEnabled(enabled)
        self.start_button.setEnabled(enabled)

    def focus_input(self):
        """Set focus to LOT input field."""
        self.lot_input.setFocus()
        self.lot_input.selectAll()

    def _set_serial_input_visible(self, visible: bool):
        """Show or hide serial input fields."""
        self.serial_label.setVisible(visible)
        self.serial_input.setVisible(visible)
        self.serial_validation_label.setVisible(False)

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
        self.process_info_label.setText(f"공정: {self._get_process_display()}")
        self.line_info_label.setText(f"생산라인: {self._get_line_display()}")
        self.equip_info_label.setText(f"장비: {self._get_equipment_display()}")
