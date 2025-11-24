"""
Home Page - Work status display and controls.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, 
    QLineEdit, QPushButton
)
from PySide6.QtCore import Qt, Signal
from widgets.work_status_card import WorkStatusCard
from widgets.base_components import ThemedLabel
from utils.theme_manager import get_theme

theme = get_theme()


class HomePage(QWidget):
    """Home page showing current work status and controls."""

    # Signals
    start_requested = Signal(str)  # lot_number
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
        grey_400 = theme.get('colors.grey.400')
        grey_300 = theme.get('colors.grey.300')
        grey_600 = theme.get('colors.grey.600')
        bg_default = theme.get('colors.background.default')
        border_default = theme.get('colors.border.default')
        border_light = theme.get('colors.border.light')
        brand = theme.get('colors.brand.main')
        brand_light = theme.get('colors.brand.light')
        success_main = theme.get('colors.success.main')
        success_dark = theme.get('colors.success.dark')
        danger_main = theme.get('colors.danger.main')
        danger_dark = theme.get('colors.danger.dark')
        text_on_dark = theme.get('colors.text.on_dark')



        # Process info section
        process_group = QFrame()
        process_group.setObjectName("process_info_frame")
        process_group.setStyleSheet(f"""
            #process_info_frame {{
                background-color: {bg_default};
                border: 1px solid {border_default};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        process_layout = QVBoxLayout(process_group)
        process_layout.setContentsMargins(16, 16, 16, 16)
        process_layout.setSpacing(8)

        # Process name
        process_name_layout = QHBoxLayout()
        process_name_label = QLabel("공정:")
        process_name_label.setStyleSheet(f"color: {grey_400}; font-size: 13px;")
        self.process_name_value = QLabel(self.config.process_name)
        self.process_name_value.setStyleSheet(f"color: {brand}; font-size: 13px; font-weight: 600;")
        process_name_layout.addWidget(process_name_label)
        process_name_layout.addWidget(self.process_name_value)
        process_name_layout.addStretch()
        process_layout.addLayout(process_name_layout)

        # Line info
        line_layout = QHBoxLayout()
        line_label = QLabel("라인:")
        line_label.setStyleSheet(f"color: {grey_400}; font-size: 13px;")
        self.line_value = QLabel(self._get_line_display())
        self.line_value.setStyleSheet(f"color: {text_primary}; font-size: 13px;")
        line_layout.addWidget(line_label)
        line_layout.addWidget(self.line_value)
        line_layout.addStretch()
        process_layout.addLayout(line_layout)

        # Equipment info
        equip_layout = QHBoxLayout()
        equip_label = QLabel("장비:")
        equip_label.setStyleSheet(f"color: {grey_400}; font-size: 13px;")
        self.equip_value = QLabel(self._get_equipment_display())
        self.equip_value.setStyleSheet(f"color: {text_primary}; font-size: 13px;")
        equip_layout.addWidget(equip_label)
        equip_layout.addWidget(self.equip_value)
        equip_layout.addStretch()
        process_layout.addLayout(equip_layout)

        layout.addWidget(process_group)

        # 2. Start Work Section
        start_group = QFrame()
        start_group.setObjectName("start_group_frame")
        start_group.setStyleSheet(f"""
            #start_group_frame {{
                background-color: {bg_default};
                border: 1px solid {border_default};
                border-radius: 8px;
            }}
        """)
        start_layout = QVBoxLayout(start_group)
        start_layout.setContentsMargins(16, 16, 16, 16)
        start_layout.setSpacing(12)

        start_title = QLabel("작업 시작")
        start_title.setStyleSheet(f"color: {grey_300}; font-size: 13px; font-weight: 600;")
        start_layout.addWidget(start_title)

        input_container = QHBoxLayout()
        input_container.setSpacing(8)

        # LOT Input
        self.lot_input = QLineEdit()
        self.lot_input.setPlaceholderText("LOT 번호 입력 또는 스캔")
        self.lot_input.setMinimumHeight(40)
        self.lot_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme.get('colors.background.elevated')};
                border: 1px solid {border_default};
                border-radius: 6px;
                padding: 0 12px;
                color: {text_primary};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {brand};
            }}
        """)
        self.lot_input.returnPressed.connect(self._on_start_clicked)
        input_container.addWidget(self.lot_input, stretch=3)

        # Start Button
        self.start_button = QPushButton("작업 시작")
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.setMinimumHeight(40)
        self.start_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {brand};
                border: none;
                border-radius: 6px;
                padding: 0 20px;
                color: {text_on_dark};
                font-size: 14px;
                font-weight: 600;
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
        input_container.addWidget(self.start_button, stretch=1)

        start_layout.addLayout(input_container)
        layout.addWidget(start_group)

        # 3. Work Status Section
        self.work_card = WorkStatusCard()
        layout.addWidget(self.work_card)

        # 4. Complete Work Section
        complete_group = QFrame()
        complete_group.setObjectName("complete_group_frame")
        complete_group.setStyleSheet(f"""
            #complete_group_frame {{
                background-color: {bg_default};
                border: 1px solid {border_default};
                border-radius: 8px;
            }}
        """)
        complete_layout = QVBoxLayout(complete_group)
        complete_layout.setContentsMargins(16, 16, 16, 16)
        complete_layout.setSpacing(12)

        complete_title = QLabel("작업 완료")
        complete_title.setStyleSheet(f"color: {grey_300}; font-size: 13px; font-weight: 600;")
        complete_layout.addWidget(complete_title)

        # PASS/FAIL buttons row
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(12)

        # PASS button
        self.pass_button = QPushButton("PASS")
        self.pass_button.setCursor(Qt.PointingHandCursor)
        self.pass_button.setMinimumHeight(48)
        self.pass_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {success_main};
                border: none;
                border-radius: 6px;
                color: {text_on_dark};
                font-size: 16px;
                font-weight: 700;
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
        self.fail_button = QPushButton("FAIL")
        self.fail_button.setCursor(Qt.PointingHandCursor)
        self.fail_button.setMinimumHeight(48)
        self.fail_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {danger_main};
                border: none;
                border-radius: 6px;
                color: {text_on_dark};
                font-size: 16px;
                font-weight: 700;
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

        complete_layout.addLayout(buttons_row)
        layout.addWidget(complete_group)

        # Status message (hidden but kept for compatibility if needed)
        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        layout.addStretch()

    def _on_start_clicked(self):
        """Handle start button click or enter press."""
        lot_number = self.lot_input.text().strip()
        if lot_number:
            self.start_requested.emit(lot_number)

    def _on_pass_clicked(self):
        """Handle PASS button click."""
        self.pass_requested.emit()

    def _on_fail_clicked(self):
        """Handle FAIL button click."""
        self.fail_requested.emit()

    def set_status(self, message: str, variant: str = "default"):
        """Set status message (No-op as label is hidden, but kept for interface compatibility)."""
        pass

    def start_work(self, lot_number: str, start_time: str):
        """Update UI for work started."""
        self.work_card.start_work(lot_number, start_time)
        
        # Disable inputs and start button, enable complete buttons
        self.lot_input.setEnabled(False)
        self.start_button.setEnabled(False)
        self.pass_button.setEnabled(True)
        self.fail_button.setEnabled(True)
        
        # Clear inputs
        self.lot_input.clear()

    def complete_work(self, complete_time: str):
        """Update UI for work completed."""
        self.work_card.complete_work(complete_time)
        
        # Enable inputs and start button, disable complete buttons
        self.lot_input.setEnabled(True)
        self.start_button.setEnabled(True)
        self.pass_button.setEnabled(False)
        self.fail_button.setEnabled(False)
        
        # Focus back to LOT input
        self.lot_input.setFocus()

    def reset(self):
        """Reset work status."""
        self.work_card.reset()
        self.lot_input.setEnabled(True)
        self.start_button.setEnabled(True)
        self.pass_button.setEnabled(False)
        self.fail_button.setEnabled(False)
        self.lot_input.clear()
        self.lot_input.setFocus()

    def set_lot_number(self, lot_number: str):
        """Set LOT number in input field."""
        self.lot_input.setText(lot_number)

    def clear_input(self):
        """Clear input fields."""
        self.lot_input.clear()

    def set_enabled(self, enabled: bool):
        """Enable or disable the start controls."""
        self.lot_input.setEnabled(enabled)
        self.start_button.setEnabled(enabled)

    def focus_input(self):
        """Set focus to LOT input field."""
        self.lot_input.setFocus()
        self.lot_input.selectAll()

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
        """Refresh displayed equipment/line info from config."""
        self.process_name_value.setText(self.config.process_name)
        self.line_value.setText(self._get_line_display())
        self.equip_value.setText(self._get_equipment_display())

    def cleanup(self):
        """Cleanup resources."""
        self.work_card.cleanup()
