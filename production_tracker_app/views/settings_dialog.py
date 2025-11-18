"""
Settings Dialog for configuration.
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox,
                               QLineEdit, QPushButton, QHBoxLayout, QGroupBox,
                               QFileDialog, QMessageBox)
import logging

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """Settings dialog for process and folder configuration."""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("설정")
        self.setModal(True)
        self.resize(500, 400)
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

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("저장")
        save_button.clicked.connect(self.save_settings)
        save_button.setStyleSheet("background-color: #3b82f6; color: white; padding: 8px;")
        cancel_button = QPushButton("취소")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def browse_folder(self):
        """Open folder browser."""
        folder = QFileDialog.getExistingDirectory(self, "폴더 선택", self.folder_input.text())
        if folder:
            self.folder_input.setText(folder)

    def save_settings(self):
        """Save settings to config."""
        try:
            self.config.process_number = self.process_combo.currentData()
            self.config.watch_folder = self.folder_input.text()
            self.config.equipment_id = self.equipment_input.text()
            self.config.line_id = self.line_input.text()
            self.config.api_base_url = self.api_input.text()

            logger.info("Settings saved successfully")
            self.accept()
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(self, "오류", f"설정 저장 실패: {str(e)}")
