"""
Defect Type Selection Dialog.
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox,
                                QTextEdit, QPushButton, QHBoxLayout)
from PySide6.QtCore import Qt
from utils.theme_manager import get_theme

theme = get_theme()


class DefectDialog(QDialog):
    """Dialog for selecting defect type when completing with FAIL."""

    def __init__(self, process_number: int, parent=None):
        super().__init__(parent)
        self.process_number = process_number
        self.selected_defect_type = None
        self.defect_description = ""

        self.setWindowTitle("불량 유형 선택")
        self.setModal(True)
        self.resize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Theme colors
        text_primary = theme.get('colors.text.primary')
        text_on_dark = theme.get('colors.text.onDark')
        text_on_brand = theme.get('colors.text.onBrand')
        grey_300 = theme.get('colors.grey.300')
        grey_400 = theme.get('colors.grey.400')
        bg_default = theme.get('colors.background.default')
        bg_elevated = theme.get('colors.background.elevated')
        bg_hover = theme.get('colors.background.hover')
        border_light = theme.get('colors.border.light')
        brand = theme.get('colors.brand.main')
        danger_main = theme.get('colors.danger.main')
        danger_dark = theme.get('colors.danger.dark')

        # Header
        header = QLabel("불량 유형 선택")
        header.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {text_primary};")
        layout.addWidget(header)

        desc = QLabel("발생한 불량의 유형을 선택하세요.")
        desc.setStyleSheet(f"color: {grey_400}; font-size: 12px;")
        layout.addWidget(desc)

        # Defect type combo
        type_label = QLabel("불량 유형")
        type_label.setStyleSheet(f"color: {grey_300}; font-size: 13px; font-weight: 500;")
        layout.addWidget(type_label)

        self.defect_combo = QComboBox()
        self.defect_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {bg_elevated};
                border: 1px solid {border_light};
                border-radius: 6px;
                padding: 8px 12px;
                color: {text_primary};
                font-size: 13px;
                min-height: 20px;
            }}
            QComboBox:focus {{
                border-color: {brand};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {grey_400};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {bg_elevated};
                border: 1px solid {border_light};
                selection-background-color: {brand};
                selection-color: {text_on_brand};
            }}
        """)

        # Add defect types based on process
        defect_types = self._get_defect_types()
        for code, name in defect_types:
            self.defect_combo.addItem(f"{code} - {name}", code)

        layout.addWidget(self.defect_combo)

        # Description input
        desc_label = QLabel("불량 설명 (선택)")
        desc_label.setStyleSheet(f"color: {grey_300}; font-size: 13px; font-weight: 500;")
        layout.addWidget(desc_label)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("추가 설명을 입력하세요...")
        self.description_input.setMaximumHeight(80)
        self.description_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg_elevated};
                border: 1px solid {border_light};
                border-radius: 6px;
                padding: 8px 12px;
                color: {text_primary};
                font-size: 13px;
            }}
            QTextEdit:focus {{
                border-color: {brand};
            }}
        """)
        layout.addWidget(self.description_input)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        cancel_button = QPushButton("취소")
        cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_elevated};
                border: 1px solid {border_light};
                border-radius: 6px;
                padding: 8px 16px;
                color: {text_primary};
                font-size: 13px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {bg_hover};
            }}
        """)
        cancel_button.clicked.connect(self.reject)

        confirm_button = QPushButton("확인")
        confirm_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {danger_main};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: {text_on_dark};
                font-size: 13px;
                font-weight: 600;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {danger_dark};
            }}
        """)
        confirm_button.clicked.connect(self._on_confirm)

        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(confirm_button)
        layout.addLayout(button_layout)

        # Apply dialog styles
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_default};
            }}
        """)

    def _get_defect_types(self) -> list:
        """Get defect types based on process number."""
        defect_types = {
            1: [
                ("MARKING_FAIL", "레이저 마킹 실패"),
            ],
            2: [
                ("PART_DEFECT", "부품 불량"),
                ("ASSEMBLY_ERROR", "조립 오류"),
            ],
            3: [
                ("SENSOR_TEMP_FAIL", "온도 센서 불량"),
                ("SENSOR_TOF_FAIL", "TOF 센서 불량"),
            ],
            4: [
                ("FIRMWARE_UPLOAD_FAIL", "펌웨어 업로드 실패"),
                ("FIRMWARE_COMM_ERROR", "통신 오류"),
            ],
            5: [
                ("ASSEMBLY_ERROR", "체결 불량"),
                ("APPEARANCE_DEFECT", "외관 손상"),
            ],
            6: [
                ("PERFORMANCE_FAIL", "성능 미달"),
            ],
            7: [
                ("LABEL_PRINT_FAIL", "라벨 인쇄 실패"),
                ("LABEL_ATTACH_ERROR", "라벨 부착 오류"),
            ],
            8: [
                ("VISUAL_DEFECT", "외관 불량"),
                ("PACKAGING_ERROR", "포장 오류"),
            ],
        }

        return defect_types.get(self.process_number, [("UNKNOWN", "알 수 없는 불량")])

    def _on_confirm(self):
        """Handle confirm button click."""
        self.selected_defect_type = self.defect_combo.currentData()
        self.defect_description = self.description_input.toPlainText().strip()
        self.accept()

    def get_result(self) -> tuple:
        """Get the selected defect type and description."""
        return (self.selected_defect_type, self.defect_description)
