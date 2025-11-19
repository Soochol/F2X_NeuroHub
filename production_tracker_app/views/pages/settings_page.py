"""
Settings Page - Inline settings configuration.
"""
import logging
from typing import Optional

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                                QComboBox, QLineEdit, QPushButton, QLabel,
                                QFileDialog, QMessageBox, QFrame)
from PySide6.QtCore import Signal

from utils.theme_manager import get_theme

logger = logging.getLogger(__name__)
theme = get_theme()

# Try to import PrintService for printer list
try:
    from services.print_service import PrintService
    PRINT_SERVICE_AVAILABLE = True
except ImportError:
    PRINT_SERVICE_AVAILABLE = False


class SettingsPage(QWidget):
    """Settings page for inline configuration."""

    # Signal emitted when settings are saved
    settings_saved = Signal()

    def __init__(self, config, print_service: Optional['PrintService'] = None, parent=None):
        super().__init__(parent)
        self.config = config
        self.print_service = print_service
        self.setup_ui()
        self._apply_styles()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Header
        header = QLabel("설정")
        header.setStyleSheet(
            f"font-size: 16px; font-weight: 600; color: {theme.get('colors.text.primary')}; margin-bottom: 8px;"
        )
        layout.addWidget(header)

        desc = QLabel("앱 환경을 설정합니다.")
        desc.setStyleSheet(f"color: {theme.get('colors.grey.400')}; font-size: 12px; margin-bottom: 16px;")
        layout.addWidget(desc)

        # Process settings
        layout.addWidget(self._create_process_section())

        # Folder settings
        layout.addWidget(self._create_folder_section())

        # Equipment settings
        layout.addWidget(self._create_equipment_section())

        # API settings
        layout.addWidget(self._create_api_section())

        # Printer settings
        layout.addWidget(self._create_printer_section())

        layout.addStretch()

        # Save button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = QPushButton("설정 저장")
        self.save_button.setObjectName("save_button")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

    def _apply_styles(self):
        """Apply styles for the settings page."""
        text_secondary = theme.get('colors.grey.300')
        bg_elevated = theme.get('colors.background.elevated')
        border_light = theme.get('colors.border.light')
        text_primary = theme.get('colors.text.primary')
        brand = theme.get('colors.brand.main')
        grey_400 = theme.get('colors.grey.400')
        text_on_brand = theme.get('colors.text.onBrand')
        bg_hover = theme.get('colors.background.hover')
        brand_light = theme.get('colors.brand.light')

        self.setStyleSheet(f"""
            QLabel {{
                color: {text_secondary};
                font-size: 13px;
            }}

            QLineEdit, QComboBox {{
                background-color: {bg_elevated};
                border: 1px solid {border_light};
                border-radius: 4px;
                padding: 6px 10px;
                color: {text_primary};
                font-size: 12px;
                min-height: 16px;
            }}

            QLineEdit:focus, QComboBox:focus {{
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

            QPushButton {{
                background-color: {bg_elevated};
                border: 1px solid {border_light};
                border-radius: 4px;
                padding: 6px 12px;
                color: {text_primary};
                font-size: 12px;
                font-weight: 500;
                min-width: 60px;
            }}

            QPushButton:hover {{
                background-color: {bg_hover};
            }}

            #save_button {{
                background-color: {brand};
                border: none;
                color: {text_on_brand};
                font-weight: 600;
                padding: 8px 20px;
            }}

            #save_button:hover {{
                background-color: {brand_light};
            }}
        """)

    def _create_section_frame(self, title: str) -> tuple:
        """Create a styled section frame with layout."""
        bg_paper = theme.get('colors.background.paper')
        border = theme.get('colors.border.default')
        brand = theme.get('colors.brand.main')

        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_paper};
                border: 1px solid {border};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {brand}; font-size: 14px; font-weight: 600; border: none;")
        layout.addWidget(title_label)

        return frame, layout

    def _create_process_section(self) -> QFrame:
        """Create process settings section."""
        frame, layout = self._create_section_frame("공정 설정")

        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        self.process_combo = QComboBox()
        process_names = {
            1: "1. 레이저 마킹", 2: "2. LMA 조립",
            3: "3. 센서 검사", 4: "4. 펌웨어 업로드",
            5: "5. 로봇 조립", 6: "6. 성능검사",
            7: "7. 라벨 프린팅", 8: "8. 포장+외관검사"
        }
        for i in range(1, 9):
            self.process_combo.addItem(process_names[i], i)
        self.process_combo.setCurrentIndex(self.config.process_number - 1)
        form_layout.addRow("공정:", self.process_combo)

        layout.addLayout(form_layout)
        return frame

    def _create_folder_section(self) -> QFrame:
        """Create folder settings section."""
        frame, layout = self._create_section_frame("파일 감시 폴더")

        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit(self.config.watch_folder)
        folder_layout.addWidget(self.folder_input)

        browse_button = QPushButton("찾아보기")
        browse_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(browse_button)

        layout.addLayout(folder_layout)
        return frame

    def _create_equipment_section(self) -> QFrame:
        """Create equipment settings section."""
        frame, layout = self._create_section_frame("설비 설정")

        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        self.equipment_input = QLineEdit(self.config.equipment_id)
        form_layout.addRow("설비 ID:", self.equipment_input)

        self.line_input = QLineEdit(self.config.line_id)
        form_layout.addRow("라인 ID:", self.line_input)

        layout.addLayout(form_layout)
        return frame

    def _create_api_section(self) -> QFrame:
        """Create API settings section."""
        frame, layout = self._create_section_frame("API 설정")

        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        self.api_input = QLineEdit(self.config.api_base_url)
        form_layout.addRow("백엔드 URL:", self.api_input)

        layout.addLayout(form_layout)
        return frame

    def _create_printer_section(self) -> QFrame:
        """Create printer settings section."""
        frame, layout = self._create_section_frame("프린터 설정")

        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        # Printer selection
        self.printer_combo = QComboBox()
        self.printer_combo.addItem("(프린터 선택)", "")
        self._populate_printers()
        form_layout.addRow("프린터:", self.printer_combo)

        # ZPL template path
        zpl_layout = QHBoxLayout()
        self.zpl_input = QLineEdit(self.config.zpl_template_path)
        self.zpl_input.setPlaceholderText("ZPL 템플릿 파일 경로 (선택)")
        zpl_layout.addWidget(self.zpl_input)

        zpl_browse_button = QPushButton("찾아보기")
        zpl_browse_button.clicked.connect(self.browse_zpl_template)
        zpl_layout.addWidget(zpl_browse_button)
        form_layout.addRow("ZPL 템플릿:", zpl_layout)

        # Test print button
        test_layout = QHBoxLayout()
        test_layout.addStretch()
        test_button = QPushButton("테스트 출력")
        test_button.clicked.connect(self.test_print)
        test_layout.addWidget(test_button)
        form_layout.addRow("", test_layout)

        layout.addLayout(form_layout)
        return frame

    def browse_folder(self):
        """Open folder browser."""
        folder = QFileDialog.getExistingDirectory(self, "폴더 선택", self.folder_input.text())
        if folder:
            self.folder_input.setText(folder)

    def browse_zpl_template(self):
        """Open file browser for ZPL template."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "ZPL 템플릿 선택",
            self.zpl_input.text(),
            "ZPL Files (*.zpl *.prn *.txt);;All Files (*)"
        )
        if file_path:
            self.zpl_input.setText(file_path)

    def _populate_printers(self):
        """Populate printer combo box with available printers."""
        printers = []

        if self.print_service:
            printers = self.print_service.get_available_printers()
        elif PRINT_SERVICE_AVAILABLE:
            try:
                temp_service = PrintService(self.config)
                printers = temp_service.get_available_printers()
            except Exception as e:
                logger.warning(f"Failed to get printer list: {e}")

        for printer in printers:
            self.printer_combo.addItem(printer, printer)

        current_printer = self.config.printer_queue
        if current_printer:
            index = self.printer_combo.findData(current_printer)
            if index >= 0:
                self.printer_combo.setCurrentIndex(index)

    def test_print(self):
        """Test print with selected printer."""
        selected_printer = self.printer_combo.currentData()

        if not selected_printer:
            QMessageBox.warning(self, "경고", "프린터를 선택해주세요.")
            return

        self.config.printer_queue = selected_printer
        self.config.zpl_template_path = self.zpl_input.text()

        if self.print_service:
            self.print_service.set_printer(selected_printer)
            success = self.print_service.test_print()
        elif PRINT_SERVICE_AVAILABLE:
            try:
                temp_service = PrintService(self.config)
                temp_service.set_printer(selected_printer)
                success = temp_service.test_print()
            except Exception as e:
                QMessageBox.critical(self, "오류", f"테스트 출력 실패: {str(e)}")
                return
        else:
            QMessageBox.warning(self, "경고", "Zebra 라이브러리가 설치되지 않았습니다.")
            return

        if success:
            QMessageBox.information(self, "성공", "테스트 라벨이 출력되었습니다.")
        else:
            QMessageBox.warning(self, "실패", "테스트 출력에 실패했습니다.")

    def save_settings(self):
        """Save settings to config."""
        try:
            self.config.process_number = self.process_combo.currentData()
            self.config.watch_folder = self.folder_input.text()
            self.config.equipment_id = self.equipment_input.text()
            self.config.line_id = self.line_input.text()
            self.config.api_base_url = self.api_input.text()
            self.config.printer_queue = self.printer_combo.currentData() or ""
            self.config.zpl_template_path = self.zpl_input.text()

            logger.info("Settings saved successfully")
            self.settings_saved.emit()
            QMessageBox.information(self, "저장 완료", "설정이 저장되었습니다. 재시작하면 적용됩니다.")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(self, "오류", f"설정 저장 실패: {str(e)}")
