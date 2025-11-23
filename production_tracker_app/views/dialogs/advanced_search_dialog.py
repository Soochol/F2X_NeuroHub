"""
Advanced Search Dialog for WIP items.

Provides comprehensive search and filtering capabilities with multiple criteria.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QDateEdit, QGroupBox, QFormLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
    QTabWidget, QWidget, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont

from utils.theme_manager import get_theme
from widgets.toast_notification import Toast
from utils.exception_handler import safe_slot

logger = logging.getLogger(__name__)
theme = get_theme()


class AdvancedSearchDialog(QDialog):
    """Advanced search dialog with multiple filter criteria."""

    # Signals
    search_executed = Signal(dict)  # Search criteria
    result_selected = Signal(dict)  # Selected result

    def __init__(self, api_client, config, parent=None):
        """
        Initialize AdvancedSearchDialog.

        Args:
            api_client: APIClient instance
            config: AppConfig instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.api_client = api_client
        self.config = config
        self.search_results: List[Dict] = []

        self.setWindowTitle("고급 검색")
        self.setMinimumSize(900, 700)
        self.setModal(True)

        self.setup_ui()
        self.load_filter_options()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        spacing = theme.get("spacing.lg", 16)
        layout.setSpacing(spacing)

        # Header
        header = QLabel("WIP 고급 검색")
        header.setProperty("variant", "page_title")
        layout.addWidget(header)

        # Tab widget for Search and History
        self.tab_widget = QTabWidget()

        # Search tab
        search_tab = self._create_search_tab()
        self.tab_widget.addTab(search_tab, "검색 조건")

        # History tab
        history_tab = self._create_history_tab()
        self.tab_widget.addTab(history_tab, "검색 히스토리")

        layout.addWidget(self.tab_widget)

        # Results section
        results_group = QGroupBox("검색 결과")
        results_layout = QVBoxLayout(results_group)

        # Result count label
        self.result_count_label = QLabel("검색 결과: 0건")
        self.result_count_label.setProperty("variant", "caption")
        results_layout.addWidget(self.result_count_label)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels([
            "Serial 번호", "LOT 번호", "제품", "공정", "상태",
            "시작 시간", "완료 시간", "경과 시간"
        ])

        header = self.results_table.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(7):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.doubleClicked.connect(self._on_result_double_clicked)

        results_layout.addWidget(self.results_table)

        layout.addWidget(results_group)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        export_btn = QPushButton("결과 내보내기")
        export_btn.setProperty("variant", "secondary")
        export_btn.clicked.connect(self._on_export_clicked)
        button_layout.addWidget(export_btn)

        close_btn = QPushButton("닫기")
        close_btn.setProperty("variant", "secondary")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _create_search_tab(self) -> QWidget:
        """Create search criteria tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Basic criteria group
        basic_group = QGroupBox("기본 검색")
        basic_layout = QFormLayout(basic_group)

        # Serial number
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("Serial 번호 (부분 일치)")
        basic_layout.addRow("Serial:", self.serial_input)

        # LOT number
        self.lot_input = QLineEdit()
        self.lot_input.setPlaceholderText("LOT 번호 (부분 일치)")
        basic_layout.addRow("LOT:", self.lot_input)

        layout.addWidget(basic_group)

        # Advanced criteria group
        advanced_group = QGroupBox("상세 필터")
        advanced_layout = QFormLayout(advanced_group)

        # Date range
        date_row = QHBoxLayout()

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        date_row.addWidget(QLabel("시작:"))
        date_row.addWidget(self.start_date)

        date_row.addWidget(QLabel("~"))

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        date_row.addWidget(QLabel("종료:"))
        date_row.addWidget(self.end_date)

        date_row.addStretch()
        advanced_layout.addRow("날짜 범위:", date_row)

        # Status filter
        self.status_combo = QComboBox()
        self.status_combo.addItems(["전체", "PASS", "FAIL", "IN_PROGRESS", "PENDING"])
        advanced_layout.addRow("상태:", self.status_combo)

        # Product filter
        self.product_combo = QComboBox()
        self.product_combo.addItem("전체")
        advanced_layout.addRow("제품:", self.product_combo)

        # Process filter
        self.process_combo = QComboBox()
        self.process_combo.addItem("전체")
        advanced_layout.addRow("공정:", self.process_combo)

        # Line filter
        self.line_combo = QComboBox()
        self.line_combo.addItem("전체")
        advanced_layout.addRow("생산라인:", self.line_combo)

        layout.addWidget(advanced_group)

        # Search options
        options_group = QGroupBox("검색 옵션")
        options_layout = QVBoxLayout(options_group)

        self.include_history_check = QCheckBox("완료된 작업 포함")
        self.include_history_check.setChecked(True)
        options_layout.addWidget(self.include_history_check)

        self.exact_match_check = QCheckBox("정확히 일치하는 결과만 표시")
        options_layout.addWidget(self.exact_match_check)

        layout.addWidget(options_group)

        # Search button
        search_btn = QPushButton("검색 실행")
        search_btn.setProperty("variant", "primary")
        search_btn.clicked.connect(self._on_search_clicked)
        search_btn.setMinimumHeight(40)
        layout.addWidget(search_btn)

        layout.addStretch()

        return widget

    def _create_history_tab(self) -> QWidget:
        """Create search history tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # History list
        self.history_list = QTableWidget()
        self.history_list.setColumnCount(3)
        self.history_list.setHorizontalHeaderLabels([
            "검색 시간", "검색 조건", "결과 수"
        ])

        header = self.history_list.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self.history_list.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_list.doubleClicked.connect(self._on_history_double_clicked)

        layout.addWidget(self.history_list)

        # Clear history button
        clear_btn = QPushButton("히스토리 지우기")
        clear_btn.setProperty("variant", "secondary")
        clear_btn.clicked.connect(self._on_clear_history_clicked)
        layout.addWidget(clear_btn)

        return widget

    def load_filter_options(self):
        """Load filter options from API."""
        try:
            # Load products
            products = self.api_client.get("/api/v1/products/active")
            for product in products:
                self.product_combo.addItem(
                    product.get("product_name", ""),
                    userData=product.get("id")
                )

            # Load processes
            processes = self.api_client.get("/api/v1/processes/active")
            for process in processes:
                process_name = process.get("process_name_ko", "")
                process_num = process.get("process_number", "")
                self.process_combo.addItem(
                    f"{process_num}. {process_name}",
                    userData=process.get("id")
                )

            # Load production lines
            lines = self.api_client.get("/api/v1/production-lines/active")
            for line in lines:
                self.line_combo.addItem(
                    f"{line.get('line_code', '')} - {line.get('line_name', '')}",
                    userData=line.get("id")
                )

        except Exception as e:
            logger.error(f"Failed to load filter options: {e}")
            Toast.warning(self, "필터 옵션을 불러오지 못했습니다")

    @safe_slot("검색 실행 실패")
    def _on_search_clicked(self):
        """Handle search button click."""
        # Build search criteria
        criteria = {
            "serial_number": self.serial_input.text().strip() or None,
            "lot_number": self.lot_input.text().strip() or None,
            "start_date": self.start_date.date().toString("yyyy-MM-dd"),
            "end_date": self.end_date.date().toString("yyyy-MM-dd"),
            "status": self.status_combo.currentText() if self.status_combo.currentIndex() > 0 else None,
            "product_id": self.product_combo.currentData() if self.product_combo.currentIndex() > 0 else None,
            "process_id": self.process_combo.currentData() if self.process_combo.currentIndex() > 0 else None,
            "line_id": self.line_combo.currentData() if self.line_combo.currentIndex() > 0 else None,
            "include_history": self.include_history_check.isChecked(),
            "exact_match": self.exact_match_check.isChecked()
        }

        # Remove None values
        criteria = {k: v for k, v in criteria.items() if v is not None}

        # Execute search
        try:
            logger.info(f"Executing search with criteria: {criteria}")

            results = self.api_client.post("/api/v1/wip-items/search", criteria)
            self.search_results = results

            # Update results table
            self._populate_results(results)

            # Add to history
            self._add_to_history(criteria, len(results))

            # Emit signal
            self.search_executed.emit(criteria)

            Toast.success(self, f"{len(results)}건의 결과를 찾았습니다")

        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            Toast.danger(self, f"검색 실패: {str(e)}")

    def _populate_results(self, results: List[Dict]):
        """
        Populate results table.

        Args:
            results: List of WIP result dictionaries
        """
        self.results_table.setRowCount(0)
        self.result_count_label.setText(f"검색 결과: {len(results)}건")

        for result in results:
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)

            # Serial number
            serial = result.get("serial_number", "")
            self.results_table.setItem(row, 0, QTableWidgetItem(serial))

            # LOT number
            lot = result.get("lot_number", "")
            self.results_table.setItem(row, 1, QTableWidgetItem(lot))

            # Product
            product = result.get("product_name", "")
            self.results_table.setItem(row, 2, QTableWidgetItem(product))

            # Process
            process = result.get("process_name", "")
            self.results_table.setItem(row, 3, QTableWidgetItem(process))

            # Status
            status = result.get("status", "")
            status_item = QTableWidgetItem(status)

            # Color code status
            if status == "PASS":
                status_item.setForeground(theme.get_qt_color("colors.semantic.success", "#10B981"))
            elif status == "FAIL":
                status_item.setForeground(theme.get_qt_color("colors.semantic.error", "#EF4444"))
            elif status == "IN_PROGRESS":
                status_item.setForeground(theme.get_qt_color("colors.semantic.warning", "#F59E0B"))

            self.results_table.setItem(row, 4, status_item)

            # Start time
            start_time = result.get("start_time", "")
            if start_time:
                start_time = datetime.fromisoformat(start_time).strftime("%Y-%m-%d %H:%M")
            self.results_table.setItem(row, 5, QTableWidgetItem(start_time))

            # Complete time
            complete_time = result.get("complete_time", "")
            if complete_time:
                complete_time = datetime.fromisoformat(complete_time).strftime("%Y-%m-%d %H:%M")
            self.results_table.setItem(row, 6, QTableWidgetItem(complete_time))

            # Elapsed time
            elapsed = self._calculate_elapsed(
                result.get("start_time"),
                result.get("complete_time")
            )
            self.results_table.setItem(row, 7, QTableWidgetItem(elapsed))

    def _calculate_elapsed(self, start_time: Optional[str], complete_time: Optional[str]) -> str:
        """Calculate elapsed time between start and complete."""
        if not start_time:
            return "-"

        try:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(complete_time) if complete_time else datetime.now()

            elapsed = end - start
            total_seconds = int(elapsed.total_seconds())

            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60

            return f"{hours}h {minutes}m"

        except Exception:
            return "-"

    def _add_to_history(self, criteria: Dict, result_count: int):
        """Add search to history."""
        row = self.history_list.rowCount()
        self.history_list.insertRow(row)

        # Search time
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history_list.setItem(row, 0, QTableWidgetItem(time_str))

        # Criteria summary
        criteria_summary = self._format_criteria(criteria)
        self.history_list.setItem(row, 1, QTableWidgetItem(criteria_summary))

        # Result count
        self.history_list.setItem(row, 2, QTableWidgetItem(str(result_count)))

        # Store full criteria in item data
        self.history_list.item(row, 0).setData(Qt.UserRole, criteria)

    def _format_criteria(self, criteria: Dict) -> str:
        """Format criteria for display."""
        parts = []

        if criteria.get("serial_number"):
            parts.append(f"Serial: {criteria['serial_number']}")
        if criteria.get("lot_number"):
            parts.append(f"LOT: {criteria['lot_number']}")
        if criteria.get("status"):
            parts.append(f"상태: {criteria['status']}")
        if criteria.get("start_date") and criteria.get("end_date"):
            parts.append(f"기간: {criteria['start_date']} ~ {criteria['end_date']}")

        return ", ".join(parts) if parts else "전체 검색"

    @safe_slot("결과 선택 실패")
    def _on_result_double_clicked(self):
        """Handle result double-click."""
        current_row = self.results_table.currentRow()
        if current_row >= 0 and current_row < len(self.search_results):
            result = self.search_results[current_row]
            self.result_selected.emit(result)
            Toast.info(self, f"선택: {result.get('serial_number', '')}")

    @safe_slot("히스토리 선택 실패")
    def _on_history_double_clicked(self):
        """Handle history double-click."""
        current_row = self.history_list.currentRow()
        if current_row >= 0:
            criteria = self.history_list.item(current_row, 0).data(Qt.UserRole)
            if criteria:
                # Restore criteria to search tab
                self._restore_criteria(criteria)
                self.tab_widget.setCurrentIndex(0)
                Toast.info(self, "검색 조건이 복원되었습니다")

    def _restore_criteria(self, criteria: Dict):
        """Restore search criteria from history."""
        if criteria.get("serial_number"):
            self.serial_input.setText(criteria["serial_number"])
        if criteria.get("lot_number"):
            self.lot_input.setText(criteria["lot_number"])
        if criteria.get("start_date"):
            self.start_date.setDate(QDate.fromString(criteria["start_date"], "yyyy-MM-dd"))
        if criteria.get("end_date"):
            self.end_date.setDate(QDate.fromString(criteria["end_date"], "yyyy-MM-dd"))
        if criteria.get("status"):
            index = self.status_combo.findText(criteria["status"])
            if index >= 0:
                self.status_combo.setCurrentIndex(index)

    def _on_clear_history_clicked(self):
        """Clear search history."""
        self.history_list.setRowCount(0)
        Toast.info(self, "검색 히스토리가 지워졌습니다")

    @safe_slot("결과 내보내기 실패")
    def _on_export_clicked(self):
        """Export search results."""
        if not self.search_results:
            Toast.warning(self, "내보낼 결과가 없습니다")
            return

        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "검색 결과 내보내기",
            f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            try:
                self._export_to_csv(file_path)
                Toast.success(self, f"결과를 내보냈습니다: {file_path}")
            except Exception as e:
                logger.error(f"Export failed: {e}")
                Toast.danger(self, f"내보내기 실패: {str(e)}")

    def _export_to_csv(self, file_path: str):
        """Export results to CSV file."""
        import csv

        with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow([
                "Serial 번호", "LOT 번호", "제품", "공정", "상태",
                "시작 시간", "완료 시간", "경과 시간"
            ])

            # Write data
            for result in self.search_results:
                writer.writerow([
                    result.get("serial_number", ""),
                    result.get("lot_number", ""),
                    result.get("product_name", ""),
                    result.get("process_name", ""),
                    result.get("status", ""),
                    result.get("start_time", ""),
                    result.get("complete_time", ""),
                    self._calculate_elapsed(
                        result.get("start_time"),
                        result.get("complete_time")
                    )
                ])

        logger.info(f"Exported {len(self.search_results)} results to {file_path}")

    def get_search_results(self) -> List[Dict]:
        """Get current search results."""
        return self.search_results
