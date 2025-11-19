"""
Start Work Page - LOT input and start button.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                                QPushButton, QFrame, QHBoxLayout)
from PySide6.QtCore import Qt, Signal


class StartWorkPage(QWidget):
    """Start work page with LOT input and start button."""

    # Signals
    start_requested = Signal(str)  # lot_number

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
        header = QLabel("착공")
        header.setStyleSheet("font-size: 16px; font-weight: 600; color: #ededed; margin-bottom: 8px;")
        layout.addWidget(header)

        desc = QLabel("LOT 바코드를 스캔하거나 입력하여 착공합니다.")
        desc.setStyleSheet("color: #9ca3af; font-size: 12px; margin-bottom: 16px;")
        layout.addWidget(desc)

        # LOT input section
        input_group = QFrame()
        input_group.setObjectName("lot_input_frame")
        input_group.setStyleSheet("""
            #lot_input_frame {
                background-color: #0a0a0a;
                border: 1px solid #1a1a1a;
                border-radius: 8px;
            }
        """)
        input_layout = QVBoxLayout(input_group)
        input_layout.setContentsMargins(16, 16, 16, 16)
        input_layout.setSpacing(12)

        # LOT input label
        lot_label = QLabel("LOT 번호")
        lot_label.setStyleSheet("color: #d1d5db; font-size: 13px; font-weight: 500;")
        input_layout.addWidget(lot_label)

        # LOT input field
        self.lot_input = QLineEdit()
        self.lot_input.setObjectName("lot_input")
        self.lot_input.setPlaceholderText("LOT 바코드를 스캔하세요...")
        self.lot_input.setStyleSheet("""
            QLineEdit {
                background-color: #1f1f1f;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
                padding: 12px 16px;
                color: #ededed;
                font-size: 14px;
                min-height: 24px;
            }
            QLineEdit:focus {
                border-color: #3ECF8E;
            }
        """)
        self.lot_input.returnPressed.connect(self._on_start_clicked)
        input_layout.addWidget(self.lot_input)

        # Start button
        self.start_button = QPushButton("착공 시작")
        self.start_button.setObjectName("start_button")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #3ECF8E;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                color: #000000;
                font-size: 14px;
                font-weight: 600;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #57D9A0;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #6b7280;
            }
        """)
        self.start_button.clicked.connect(self._on_start_clicked)
        input_layout.addWidget(self.start_button)

        layout.addWidget(input_group)

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
            "• 바코드 스캐너로 LOT 바코드를 스캔하면 자동 입력됩니다.\n"
            "• Enter 키를 누르거나 '착공 시작' 버튼을 클릭하여 착공합니다.\n"
            "• 착공 후에는 완공 메뉴에서 작업을 완료할 수 있습니다."
        )
        info_text.setStyleSheet("color: #9ca3af; font-size: 12px; line-height: 1.5;")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)

        layout.addWidget(info_frame)

        layout.addStretch()

    def _on_start_clicked(self):
        """Handle start button click."""
        lot_number = self.lot_input.text().strip()
        if lot_number:
            self.start_requested.emit(lot_number)

    def set_lot_number(self, lot_number: str):
        """Set LOT number in input field."""
        self.lot_input.setText(lot_number)

    def clear_input(self):
        """Clear input field."""
        self.lot_input.clear()

    def set_enabled(self, enabled: bool):
        """Enable or disable the start controls."""
        self.lot_input.setEnabled(enabled)
        self.start_button.setEnabled(enabled)

    def focus_input(self):
        """Set focus to LOT input field."""
        self.lot_input.setFocus()
        self.lot_input.selectAll()
