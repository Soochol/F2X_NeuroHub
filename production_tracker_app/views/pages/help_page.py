"""
Help Page - Usage guide and information.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame,
                                QScrollArea)
from PySide6.QtCore import Qt


class HelpPage(QWidget):
    """Help page with usage guide."""

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
        header = QLabel("도움말")
        header.setStyleSheet("font-size: 16px; font-weight: 600; color: #ededed; margin-bottom: 8px;")
        layout.addWidget(header)

        desc = QLabel("Production Tracker 사용 가이드입니다.")
        desc.setStyleSheet("color: #9ca3af; font-size: 12px; margin-bottom: 16px;")
        layout.addWidget(desc)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #1a1a1a;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #3a3a3a;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4a4a4a;
            }
        """)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 8, 0)
        content_layout.setSpacing(16)

        # Basic usage section
        content_layout.addWidget(self._create_section(
            "기본 사용법",
            [
                ("1. 착공", "착공 메뉴에서 LOT 바코드를 스캔하고 '착공 시작' 버튼을 클릭합니다."),
                ("2. 작업 수행", "해당 공정의 작업을 수행합니다."),
                ("3. 완공", "완공 메뉴에서 'PASS 완공' 또는 'FAIL 완공' 버튼을 클릭합니다."),
            ]
        ))

        # Barcode scanning section
        content_layout.addWidget(self._create_section(
            "바코드 스캔",
            [
                ("자동 입력", "바코드 스캐너로 LOT 바코드를 스캔하면 자동으로 입력됩니다."),
                ("수동 입력", "키보드로 LOT 번호를 직접 입력할 수도 있습니다."),
                ("Enter 키", "Enter 키를 누르면 착공이 시작됩니다."),
            ]
        ))

        # Defect types section
        content_layout.addWidget(self._create_section(
            "불량 유형",
            self._get_defect_types_for_process()
        ))

        # Status section
        content_layout.addWidget(self._create_section(
            "상태 표시",
            [
                ("온라인", "서버와 정상 연결된 상태입니다."),
                ("오프라인", "서버와 연결이 끊긴 상태입니다. 네트워크를 확인하세요."),
                ("착공중", "현재 작업이 진행 중입니다."),
            ]
        ))

        # Keyboard shortcuts section
        content_layout.addWidget(self._create_section(
            "단축키",
            [
                ("Enter", "착공 시작 (LOT 입력 후)"),
                ("Esc", "현재 작업 취소"),
            ]
        ))

        content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

    def _create_section(self, title: str, items: list) -> QFrame:
        """Create a help section with title and items."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #0a0a0a;
                border: 1px solid #1a1a1a;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #3ECF8E; font-size: 14px; font-weight: 600;")
        layout.addWidget(title_label)

        # Items
        for item_title, item_desc in items:
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(4)

            item_title_label = QLabel(item_title)
            item_title_label.setStyleSheet("color: #d1d5db; font-size: 13px; font-weight: 500;")
            item_layout.addWidget(item_title_label)

            item_desc_label = QLabel(item_desc)
            item_desc_label.setStyleSheet("color: #9ca3af; font-size: 12px;")
            item_desc_label.setWordWrap(True)
            item_layout.addWidget(item_desc_label)

            layout.addWidget(item_widget)

        return frame

    def _get_defect_types_for_process(self) -> list:
        """Get defect types based on current process."""
        process_num = self.config.process_number

        defect_types = {
            1: [
                ("MARKING_FAIL", "레이저 마킹 실패"),
            ],
            2: [
                ("PART_DEFECT", "부품 불량 (SMA 스프링, 플라스틱 부품)"),
                ("ASSEMBLY_ERROR", "조립 오류 (체결 실패, 순서 오류)"),
            ],
            3: [
                ("SENSOR_TEMP_FAIL", "온도 센서 범위 초과"),
                ("SENSOR_TOF_FAIL", "TOF 센서 I2C 통신 실패"),
            ],
            4: [
                ("FIRMWARE_UPLOAD_FAIL", "펌웨어 업로드 실패"),
                ("FIRMWARE_COMM_ERROR", "통신 오류 (케이블, 포트)"),
            ],
            5: [
                ("ASSEMBLY_ERROR", "체결 불량"),
                ("APPEARANCE_DEFECT", "외관 손상 (스크래치, 손상)"),
            ],
            6: [
                ("PERFORMANCE_FAIL", "성능 측정치 미달"),
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

        return defect_types.get(process_num, [("UNKNOWN", "알 수 없는 불량")])
