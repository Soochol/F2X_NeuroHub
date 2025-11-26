"""
WIP Generation Page for Production Tracker App.

Allows selecting LOTs and generating WIP with barcode printing.
"""
import logging
from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout, QHeaderView, QLabel, QMessageBox, QProgressDialog,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
)

from utils.exception_handler import safe_slot
from utils.theme_manager import get_theme
from widgets.toast_notification import Toast

logger = logging.getLogger(__name__)
theme = get_theme()


class WIPGenerationPage(QWidget):
    """WIP Generation page with LOT selection and generation."""

    # Signals
    refresh_requested = Signal()

    def __init__(self, viewmodel: Any, config: Any) -> None:
        """
        Initialize WIPGenerationPage.

        Args:
            viewmodel: WIPGenerationViewModel instance
            config: AppConfig instance
        """
        super().__init__()
        self.viewmodel = viewmodel
        self.config = config
        self.selected_lot_id: int = 0
        self.progress_dialog: Optional[QProgressDialog] = None

        self.setup_ui()
        self.connect_signals()

        # Load LOTs on initialization
        self.viewmodel.load_lots("CREATED")

    def setup_ui(self) -> None:
        """Setup UI components."""
        layout = QVBoxLayout(self)
        spacing = theme.get("spacing.lg", 16)
        layout.setSpacing(spacing)
        layout.setContentsMargins(spacing, spacing, spacing, spacing)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("WIP 생성")
        title.setProperty("variant", "page_title")
        header_layout.addWidget(title)

        header_layout.addStretch()

        refresh_btn = QPushButton("새로고침")
        refresh_btn.setProperty("variant", "secondary")
        refresh_btn.clicked.connect(self._on_refresh_clicked)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Info label
        info_label = QLabel("CREATED 상태의 LOT를 선택하고 WIP를 생성하세요")
        info_label.setProperty("variant", "help_text")
        layout.addWidget(info_label)

        # LOT table
        self.lot_table = QTableWidget()
        self.lot_table.setColumnCount(6)
        self.lot_table.setHorizontalHeaderLabels([
            "LOT 번호", "제품명", "목표 수량", "생성일", "상태", "ID"
        ])

        # Table styling
        header = self.lot_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # LOT 번호
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 제품명
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 목표 수량
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 생성일
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 상태
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # ID

        self.lot_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.lot_table.setSelectionMode(QTableWidget.SingleSelection)
        self.lot_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.lot_table.setAlternatingRowColors(True)

        # Double-click to generate
        self.lot_table.doubleClicked.connect(self._on_lot_double_clicked)

        layout.addWidget(self.lot_table)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.generate_btn = QPushButton("WIP 생성")
        self.generate_btn.setProperty("variant", "primary")
        self.generate_btn.setEnabled(False)
        self.generate_btn.clicked.connect(self._on_generate_clicked)
        button_layout.addWidget(self.generate_btn)

        layout.addLayout(button_layout)

        # Connect table selection
        self.lot_table.itemSelectionChanged.connect(self._on_selection_changed)

    def connect_signals(self) -> None:
        """Connect ViewModel signals."""
        self.viewmodel.lots_loaded.connect(self._on_lots_loaded)
        self.viewmodel.wip_generation_started.connect(self._on_generation_started)
        self.viewmodel.wip_generation_progress.connect(self._on_generation_progress)
        self.viewmodel.wip_generation_completed.connect(self._on_generation_completed)
        self.viewmodel.error_occurred.connect(self._on_error)

    @safe_slot("LOT 목록 로드 실패")
    def _on_lots_loaded(self, lots: List[Dict[str, Any]]) -> None:
        """Handle LOTs loaded."""
        logger.info(f"Loaded {len(lots)} LOTs")

        # Clear table
        self.lot_table.setRowCount(0)

        # Populate table
        for lot in lots:
            row = self.lot_table.rowCount()
            self.lot_table.insertRow(row)

            # LOT 번호
            lot_number = lot.get("lot_number", "")
            self.lot_table.setItem(row, 0, QTableWidgetItem(lot_number))

            # 제품명
            product_name = lot.get("product_name", "")
            self.lot_table.setItem(row, 1, QTableWidgetItem(product_name))

            # 목표 수량
            target_quantity = lot.get("target_quantity", 0)
            self.lot_table.setItem(row, 2, QTableWidgetItem(str(target_quantity)))

            # 생성일
            created_at = lot.get("created_at", "")
            if created_at:
                # Format datetime
                created_date = created_at.split("T")[0] if "T" in created_at else created_at
                self.lot_table.setItem(row, 3, QTableWidgetItem(created_date))
            else:
                self.lot_table.setItem(row, 3, QTableWidgetItem(""))

            # 상태
            status = lot.get("status", "")
            self.lot_table.setItem(row, 4, QTableWidgetItem(status))

            # ID (hidden)
            lot_id = lot.get("id", 0)
            id_item = QTableWidgetItem(str(lot_id))
            self.lot_table.setItem(row, 5, id_item)

        # Hide ID column
        self.lot_table.setColumnHidden(5, True)

        Toast.info(self, f"{len(lots)}개 LOT 로드됨")

    def _on_selection_changed(self) -> None:
        """Handle table selection change."""
        selected_rows = self.lot_table.selectedIndexes()
        self.generate_btn.setEnabled(len(selected_rows) > 0)

    def _on_refresh_clicked(self) -> None:
        """Handle refresh button click."""
        self.viewmodel.load_lots("CREATED")
        self.refresh_requested.emit()

    def _on_lot_double_clicked(self) -> None:
        """Handle LOT double-click."""
        self._on_generate_clicked()

    def _on_generate_clicked(self) -> None:
        """Handle generate button click."""
        selected_rows = self.lot_table.selectionModel().selectedRows()
        if not selected_rows:
            Toast.warning(self, "LOT를 선택하세요")
            return

        # Get selected LOT ID
        row = selected_rows[0].row()
        lot_id_item = self.lot_table.item(row, 5)
        lot_id = int(lot_id_item.text())

        lot_number_item = self.lot_table.item(row, 0)
        lot_number = lot_number_item.text()

        # Confirm dialog
        reply = QMessageBox.question(
            self,
            "WIP 생성 확인",
            f"LOT {lot_number}에 대해 WIP를 생성하시겠습니까?\n\n"
            f"생성된 Serial 번호로 바코드가 출력됩니다.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.selected_lot_id = lot_id
            self.viewmodel.start_wip_generation(lot_id)

    @safe_slot("WIP 생성 시작 실패")
    def _on_generation_started(self) -> None:
        """Handle generation started."""
        logger.info("WIP generation started")

        # Show progress dialog
        self.progress_dialog = QProgressDialog(
            "WIP 생성 중...",
            "취소",
            0,
            100,
            self
        )
        self.progress_dialog.setWindowTitle("WIP 생성")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.show()

        # Disable generate button
        self.generate_btn.setEnabled(False)

    @safe_slot("진행률 업데이트 실패")
    def _on_generation_progress(self, percentage: int, message: str) -> None:
        """Handle generation progress."""
        if self.progress_dialog:
            self.progress_dialog.setValue(percentage)
            self.progress_dialog.setLabelText(message)

    @safe_slot("WIP 생성 완료 처리 실패")
    def _on_generation_completed(self, result: Dict[str, Any]) -> None:
        """Handle generation completed."""
        generated_serials = result.get("generated_serials", [])
        count = len(generated_serials)

        logger.info(f"WIP generation completed: {count} serials")

        # Close progress dialog
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None

        # Show success message
        QMessageBox.information(
            self,
            "WIP 생성 완료",
            f"{count}개의 Serial이 생성되었습니다.\n\n"
            f"바코드 출력이 완료되었습니다.",
            QMessageBox.Ok
        )

        Toast.success(self, f"{count}개 WIP 생성 완료")

        # Re-enable generate button
        self.generate_btn.setEnabled(True)

        # Clear selection
        self.lot_table.clearSelection()

    @safe_slot("에러 처리 실패")
    def _on_error(self, error_msg: str) -> None:
        """Handle error."""
        logger.error(f"Error: {error_msg}")

        # Close progress dialog
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None

        # Show error message
        QMessageBox.critical(
            self,
            "WIP 생성 실패",
            error_msg,
            QMessageBox.Ok
        )

        Toast.danger(self, f"오류: {error_msg}")

        # Re-enable generate button
        self.generate_btn.setEnabled(True)

    def cleanup(self) -> None:
        """Clean up resources."""
        if self.progress_dialog:
            self.progress_dialog.close()
        self.viewmodel.cleanup()
