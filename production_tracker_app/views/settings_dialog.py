"""
Settings Dialog for configuration.
"""
import logging
from typing import Optional

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox,
                               QLineEdit, QPushButton, QHBoxLayout, QGroupBox,
                               QFileDialog, QMessageBox, QLabel)

logger = logging.getLogger(__name__)

# Try to import PrintService for printer list
try:
    from services.print_service import PrintService
    PRINT_SERVICE_AVAILABLE = True
except ImportError:
    PRINT_SERVICE_AVAILABLE = False


class SettingsDialog(QDialog):
    """Settings dialog for process and folder configuration."""

    def __init__(self, config, print_service: Optional['PrintService'] = None, parent=None):
        super().__init__(parent)
        self.config = config
        self.print_service = print_service
        self.setWindowTitle("환경설정")
        self.setModal(True)
        self.resize(450, 550)
        self.setup_ui()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)

        # Process selection
        process_group = QGroupBox("공정 설정")
        process_layout = QFormLayout(process_group)

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
        process_layout.addRow("공정 선택:", self.process_combo)

        layout.addWidget(process_group)

        # Watch folder
        folder_group = QGroupBox("파일 감시 폴더")
        folder_layout = QVBoxLayout(folder_group)

        folder_input_layout = QHBoxLayout()
        self.folder_input = QLineEdit(self.config.watch_folder)
        folder_input_layout.addWidget(self.folder_input)

        browse_button = QPushButton("찾아보기")
        browse_button.clicked.connect(self.browse_folder)
        folder_input_layout.addWidget(browse_button)

        folder_layout.addLayout(folder_input_layout)
        layout.addWidget(folder_group)

        # Equipment settings
        equipment_group = QGroupBox("설비 설정")
        equipment_layout = QFormLayout(equipment_group)

        self.equipment_input = QLineEdit(self.config.equipment_id)
        equipment_layout.addRow("설비 ID:", self.equipment_input)

        self.line_input = QLineEdit(self.config.line_id)
        equipment_layout.addRow("라인 ID:", self.line_input)

        layout.addWidget(equipment_group)

        # API settings
        api_group = QGroupBox("API 설정")
        api_layout = QFormLayout(api_group)

        self.api_input = QLineEdit(self.config.api_base_url)
        api_layout.addRow("백엔드 URL:", self.api_input)

        layout.addWidget(api_group)

        # Printer settings (for Process 7 - Label Printing)
        printer_group = QGroupBox("프린터 설정 (라벨 프린팅)")
        printer_layout = QFormLayout(printer_group)

        # Printer selection
        self.printer_combo = QComboBox()
        self.printer_combo.addItem("(프린터 선택)", "")
        self._populate_printers()
        printer_layout.addRow("프린터:", self.printer_combo)

        # ZPL template path
        zpl_layout = QHBoxLayout()
        self.zpl_input = QLineEdit(self.config.zpl_template_path)
        self.zpl_input.setPlaceholderText("ZPL 템플릿 파일 경로 (선택)")
        zpl_layout.addWidget(self.zpl_input)

        zpl_browse_button = QPushButton("찾아보기")
        zpl_browse_button.clicked.connect(self.browse_zpl_template)
        zpl_layout.addWidget(zpl_browse_button)
        printer_layout.addRow("ZPL 템플릿:", zpl_layout)

        # Test print button
        test_print_layout = QHBoxLayout()
        test_print_button = QPushButton("테스트 출력")
        test_print_button.clicked.connect(self.test_print)
        test_print_layout.addStretch()
        test_print_layout.addWidget(test_print_button)
        printer_layout.addRow("", test_print_layout)

        layout.addWidget(printer_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        save_button = QPushButton("저장")
        save_button.setObjectName("save_button")
        save_button.setProperty("variant", "primary")
        save_button.clicked.connect(self.save_settings)

        cancel_button = QPushButton("취소")
        cancel_button.setObjectName("cancel_button")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        layout.addLayout(button_layout)

    def browse_folder(self):
        """Open folder browser."""
        folder = QFileDialog.getExistingDirectory(self, "폴더 선택", self.folder_input.text())
        if folder:
            self.folder_input.setText(folder)

    def _populate_printers(self):
        """Populate printer combo box with available printers."""
        printers = []

        # Get printers from PrintService if available
        if self.print_service:
            printers = self.print_service.get_available_printers()
        elif PRINT_SERVICE_AVAILABLE:
            # Create temporary PrintService to get printer list
            try:
                temp_service = PrintService(self.config)
                printers = temp_service.get_available_printers()
            except Exception as e:
                logger.warning(f"Failed to get printer list: {e}")

        # Add printers to combo
        for printer in printers:
            self.printer_combo.addItem(printer, printer)

        # Select current printer
        current_printer = self.config.printer_queue
        if current_printer:
            index = self.printer_combo.findData(current_printer)
            if index >= 0:
                self.printer_combo.setCurrentIndex(index)

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

    def test_print(self):
        """Test print with selected printer."""
        selected_printer = self.printer_combo.currentData()

        if not selected_printer:
            QMessageBox.warning(self, "경고", "프린터를 선택해주세요.")
            return

        # Save printer setting temporarily
        self.config.printer_queue = selected_printer
        self.config.zpl_template_path = self.zpl_input.text()

        if self.print_service:
            # Use existing print service
            self.print_service.set_printer(selected_printer)
            success = self.print_service.test_print()
        elif PRINT_SERVICE_AVAILABLE:
            # Create temporary print service
            try:
                temp_service = PrintService(self.config)
                temp_service.set_printer(selected_printer)
                success = temp_service.test_print()
            except Exception as e:
                QMessageBox.critical(self, "오류", f"테스트 출력 실패: {str(e)}")
                return
        else:
            QMessageBox.warning(self, "경고", "Zebra 라이브러리가 설치되지 않았습니다.\npip install zebra")
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

            # Save printer settings
            self.config.printer_queue = self.printer_combo.currentData() or ""
            self.config.zpl_template_path = self.zpl_input.text()

            logger.info("Settings saved successfully")
            self.accept()
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(self, "오류", f"설정 저장 실패: {str(e)}")
