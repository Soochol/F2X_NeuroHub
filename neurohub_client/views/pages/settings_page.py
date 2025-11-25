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
from services.api_client import APIClient

logger = logging.getLogger(__name__)
theme = get_theme()


class SettingsPage(QWidget):
    """Settings page for inline configuration."""

    # Signal emitted when settings are saved
    settings_saved = Signal()
    # Signal emitted when data is refreshed from API
    data_refreshed = Signal(str, int)  # (data_type, count)

    def __init__(self, config, api_client: Optional[APIClient] = None, parent=None):
        super().__init__(parent)
        self.config = config
        self.api_client = api_client

        # Cache for API data
        self._production_lines = []
        self._equipment_list = []
        self._processes = []
        self._is_loading = True  # Start with True to prevent saves during init

        self.setup_ui()
        self._apply_styles()

        # Load data from API after UI setup
        self._load_api_data()
        
        # Ensure loading flag is reset if it wasn't already
        if self._is_loading and not self.api_client:
             self._is_loading = False

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

        # TCP Communication settings
        layout.addWidget(self._create_tcp_section())

        layout.addStretch()


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
                padding: 0 10px;
                color: {text_primary};
                font-size: 12px;
                height: 32px;
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
                padding: 0 12px;
                color: {text_primary};
                font-size: 12px;
                font-weight: 500;
                min-width: 60px;
                height: 32px;
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

        # Process selection with refresh button
        process_layout = QHBoxLayout()
        self.process_combo = QComboBox()
        self.process_combo.currentIndexChanged.connect(self.save_settings)
        self.process_combo.addItem("(공정 선택)", None)
        process_layout.addWidget(self.process_combo, 1)

        # Refresh button for processes
        process_refresh_btn = QPushButton("새로고침")
        process_refresh_btn.setFixedWidth(70)
        process_refresh_btn.clicked.connect(self._refresh_processes)
        process_layout.addWidget(process_refresh_btn)

        form_layout.addRow("공정:", process_layout)

        layout.addLayout(form_layout)
        return frame

    def _create_folder_section(self) -> QFrame:
        """Create folder settings section."""
        frame, layout = self._create_section_frame("파일 감시 폴더")

        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit(self.config.watch_folder)
        self.folder_input.textChanged.connect(self.save_settings)
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

        # Production line selection
        line_layout = QHBoxLayout()
        self.line_combo = QComboBox()
        self.line_combo.currentIndexChanged.connect(self.save_settings)
        self.line_combo.addItem("(생산라인 선택)", None)
        line_layout.addWidget(self.line_combo, 1)

        # Refresh button for production lines
        line_refresh_btn = QPushButton("새로고침")
        line_refresh_btn.setFixedWidth(70)
        line_refresh_btn.clicked.connect(self._refresh_production_lines)
        line_layout.addWidget(line_refresh_btn)

        form_layout.addRow("생산라인:", line_layout)

        # Equipment selection
        equip_layout = QHBoxLayout()
        self.equipment_combo = QComboBox()
        self.equipment_combo.currentIndexChanged.connect(self.save_settings)
        self.equipment_combo.addItem("(장비 선택)", None)
        equip_layout.addWidget(self.equipment_combo, 1)

        # Refresh button for equipment
        equip_refresh_btn = QPushButton("새로고침")
        equip_refresh_btn.setFixedWidth(70)
        equip_refresh_btn.clicked.connect(self._refresh_equipment)
        equip_layout.addWidget(equip_refresh_btn)

        form_layout.addRow("장비:", equip_layout)

        layout.addLayout(form_layout)
        return frame

    def _load_api_data(self):
        """Load processes, production lines and equipment from API."""
        if not self.api_client:
            logger.warning("API client not available, skipping data load")
            return

        self._refresh_processes()
        self._refresh_production_lines()
        self._refresh_equipment()

    def _refresh_processes(self):
        """Refresh processes from API."""
        if not self.api_client:
            QMessageBox.warning(self, "경고", "API 클라이언트가 설정되지 않았습니다.")
            return

        self._is_loading = True
        try:
            self._processes = self.api_client.get_processes()

            # Clear and repopulate combo
            self.process_combo.clear()
            self.process_combo.addItem("(공정 선택)", None)

            for process in self._processes:
                process_num = process.get('process_number', 0)
                process_name = process.get('process_name_ko', '')
                display_text = f"{process_num}. {process_name}"
                self.process_combo.addItem(display_text, process)
                logger.debug(f"Added process item: '{display_text}'")

            # Log combo box state
            logger.info(f"Process combo count: {self.process_combo.count()}")

            # Restore saved selection
            saved_id = self.config.process_db_id
            logger.debug(f"Saved process_db_id: {saved_id}, process_number: {self.config.process_number}")

            if saved_id:
                for i in range(1, self.process_combo.count()):
                    data = self.process_combo.itemData(i)
                    if data and data.get('id') == saved_id:
                        self.process_combo.setCurrentIndex(i)
                        logger.debug(f"Restored selection by db_id: index {i}")
                        break
            else:
                # Fallback to process_number if db_id not set
                saved_number = self.config.process_number
                if saved_number:
                    for i in range(1, self.process_combo.count()):
                        data = self.process_combo.itemData(i)
                        if data and data.get('process_number') == saved_number:
                            self.process_combo.setCurrentIndex(i)
                            logger.debug(f"Restored selection by process_number: index {i}")
                            break

            # Force UI update
            self.process_combo.update()

            logger.info(f"Loaded {len(self._processes)} processes, current index: {self.process_combo.currentIndex()}")
            self.data_refreshed.emit("공정", len(self._processes))

        except Exception as e:
            logger.error(f"Failed to load processes: {e}")
            QMessageBox.warning(self, "오류", f"공정 목록 로드 실패: {str(e)}")
        finally:
            self._is_loading = False

    def _refresh_production_lines(self):
        """Refresh production lines from API."""
        if not self.api_client:
            QMessageBox.warning(self, "경고", "API 클라이언트가 설정되지 않았습니다.")
            return

        self._is_loading = True
        try:
            self._production_lines = self.api_client.get_production_lines()

            # Clear and repopulate combo
            self.line_combo.clear()
            self.line_combo.addItem("(생산라인 선택)", None)

            for line in self._production_lines:
                display_text = f"{line['line_code']} - {line['line_name']}"
                self.line_combo.addItem(display_text, line)

            # Restore saved selection
            saved_id = self.config.line_id
            if saved_id:
                for i in range(1, self.line_combo.count()):
                    data = self.line_combo.itemData(i)
                    if data and data.get('id') == saved_id:
                        self.line_combo.setCurrentIndex(i)
                        break

            logger.info(f"Loaded {len(self._production_lines)} production lines")
            self.data_refreshed.emit("생산라인", len(self._production_lines))

        except Exception as e:
            logger.error(f"Failed to load production lines: {e}")
            QMessageBox.warning(self, "오류", f"생산라인 목록 로드 실패: {str(e)}")
        finally:
            self._is_loading = False

    def _refresh_equipment(self):
        """Refresh equipment list from API."""
        if not self.api_client:
            QMessageBox.warning(self, "경고", "API 클라이언트가 설정되지 않았습니다.")
            return

        self._is_loading = True
        try:
            self._equipment_list = self.api_client.get_equipment()

            # Clear and repopulate combo
            self.equipment_combo.clear()
            self.equipment_combo.addItem("(장비 선택)", None)

            for equip in self._equipment_list:
                display_text = f"{equip['equipment_code']} - {equip['equipment_name']}"
                self.equipment_combo.addItem(display_text, equip)

            # Restore saved selection
            saved_id = self.config.equipment_id
            if saved_id:
                for i in range(1, self.equipment_combo.count()):
                    data = self.equipment_combo.itemData(i)
                    if data and data.get('id') == saved_id:
                        self.equipment_combo.setCurrentIndex(i)
                        break

            logger.info(f"Loaded {len(self._equipment_list)} equipment")
            self.data_refreshed.emit("장비", len(self._equipment_list))

        except Exception as e:
            logger.error(f"Failed to load equipment: {e}")
            QMessageBox.warning(self, "오류", f"장비 목록 로드 실패: {str(e)}")
        finally:
            self._is_loading = False

    def _create_api_section(self) -> QFrame:
        """Create API settings section."""
        frame, layout = self._create_section_frame("API 설정")

        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        self.api_input = QLineEdit(self.config.api_base_url)
        self.api_input.textChanged.connect(self.save_settings)
        form_layout.addRow("백엔드 URL:", self.api_input)

        layout.addLayout(form_layout)
        return frame

    def _create_tcp_section(self) -> QFrame:
        """Create TCP server settings section."""
        frame, layout = self._create_section_frame("TCP 통신 설정")

        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        self.tcp_port_input = QLineEdit(str(self.config.tcp_port))
        self.tcp_port_input.setPlaceholderText("기본값: 9000")
        self.tcp_port_input.textChanged.connect(self.save_settings)
        form_layout.addRow("TCP 포트:", self.tcp_port_input)

        layout.addLayout(form_layout)
        return frame

    def browse_folder(self):
        """Open folder browser."""
        folder = QFileDialog.getExistingDirectory(self, "폴더 선택", self.folder_input.text())
        if folder:
            self.folder_input.setText(folder)

    def save_settings(self):
        """Save settings to config."""
        if self._is_loading:
            return

        try:
            # Save process selection
            process_data = self.process_combo.currentData()
            if process_data:
                self.config.process_db_id = process_data.get('id', 0)
                self.config.process_number = process_data.get('process_number', 1)
                self.config.process_code = process_data.get('process_code', '')
                self.config.process_name = process_data.get('process_name_ko', '')
                self.config.process_name_en = process_data.get('process_name_en', '')
            else:
                self.config.process_db_id = 0
                self.config.process_number = 1
                self.config.process_code = ''
                self.config.process_name = ''
                self.config.process_name_en = ''

            self.config.watch_folder = self.folder_input.text()

            # Save production line selection
            line_data = self.line_combo.currentData()
            if line_data:
                self.config.line_id = line_data.get('id', 0)
                self.config.line_code = line_data.get('line_code', '')
                self.config.line_name = line_data.get('line_name', '')
            else:
                self.config.line_id = 0
                self.config.line_code = ''
                self.config.line_name = ''

            # Save equipment selection
            equip_data = self.equipment_combo.currentData()
            if equip_data:
                self.config.equipment_id = equip_data.get('id', 0)
                self.config.equipment_code = equip_data.get('equipment_code', '')
                self.config.equipment_name = equip_data.get('equipment_name', '')
            else:
                self.config.equipment_id = 0
                self.config.equipment_code = ''
                self.config.equipment_name = ''

            self.config.api_base_url = self.api_input.text()

            # Save TCP port
            try:
                tcp_port = int(self.tcp_port_input.text())
                if not 1 <= tcp_port <= 65535:
                    QMessageBox.warning(self, "경고", "TCP 포트는 1~65535 범위여야 합니다.")
                    return
                self.config.tcp_port = tcp_port
            except ValueError:
                QMessageBox.warning(self, "경고", "TCP 포트는 숫자여야 합니다.")
                return

            logger.info("Settings saved successfully")
            self.settings_saved.emit()
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(self, "오류", f"설정 저장 실패: {str(e)}")
