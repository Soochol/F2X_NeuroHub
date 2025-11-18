"""History Dialog - Process history viewer"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QComboBox, QDateEdit, QLabel, QHeaderView, QMessageBox,
    QProgressBar
)
from PySide6.QtCore import Qt, QDate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HistoryDialog(QDialog):
    """작업 이력 조회 다이얼로그"""

    def __init__(self, history_service, config, app_state, parent=None):
        super().__init__(parent)
        self.history_service = history_service
        self.config = config
        self.app_state = app_state
        self._history_worker = None  # Track worker thread
        self.setup_ui()
        self.load_initial_data()

    def setup_ui(self):
        """Setup user interface"""
        self.setWindowTitle("작업 이력")
        self.setMinimumSize(1200, 700)

        layout = QVBoxLayout(self)

        # Filter section
        filter_layout = QHBoxLayout()

        # Date range filter
        filter_layout.addWidget(QLabel("기간:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        filter_layout.addWidget(self.start_date)

        filter_layout.addWidget(QLabel("~"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        filter_layout.addWidget(self.end_date)

        # Result filter
        filter_layout.addWidget(QLabel("결과:"))
        self.result_filter = QComboBox()
        self.result_filter.addItems(["전체", "PASS", "FAIL", "REWORK"])
        filter_layout.addWidget(self.result_filter)

        # Search button
        self.search_btn = QPushButton("🔍 조회")
        self.search_btn.clicked.connect(self.load_history)
        filter_layout.addWidget(self.search_btn)

        filter_layout.addStretch()

        # Export button
        self.export_btn = QPushButton("📊 Excel 내보내기")
        self.export_btn.clicked.connect(self.export_to_excel)
        filter_layout.addWidget(self.export_btn)

        layout.addLayout(filter_layout)

        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(9)
        self.history_table.setHorizontalHeaderLabels([
            "일시", "LOT 번호", "Serial 번호", "공정",
            "작업자", "소요시간", "결과", "측정값", "비고"
        ])

        # Column sizing
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.Stretch)
        header.setSectionResizeMode(8, QHeaderView.Stretch)

        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setSortingEnabled(True)

        layout.addWidget(self.history_table)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Status bar
        self.status_label = QLabel("준비")
        layout.addWidget(self.status_label)

        # Close button
        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def load_initial_data(self):
        """초기 데이터 로드 (최근 7일)"""
        self.load_history()

    def load_history(self):
        """이력 조회 - Non-blocking with QThread"""
        from workers import HistoryLoaderWorker

        # Cancel existing worker if running
        if self._history_worker and self._history_worker.isRunning():
            self._history_worker.cancel()
            self._history_worker.quit()
            self._history_worker.wait()

        # UI feedback
        self.search_btn.setEnabled(False)
        self.status_label.setText("조회 중...")
        self.history_table.setSortingEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Get filter values
        start_date = self.start_date.date().toPython()
        end_date = self.end_date.date().toPython()
        result_filter = self.result_filter.currentText()
        if result_filter == "전체":
            result_filter = None

        # Create worker thread
        self._history_worker = HistoryLoaderWorker(
            self.history_service,
            process_id=self.config.process_number,
            start_date=start_date,
            end_date=end_date,
            result_filter=result_filter,
            limit=500
        )

        # Connect worker signals
        self._history_worker.data_ready.connect(self._on_history_loaded)
        self._history_worker.error.connect(self._on_history_error)
        self._history_worker.progress.connect(self._on_progress_update)
        self._history_worker.finished.connect(self._on_worker_finished)

        # Start worker
        self._history_worker.start()

    def _on_history_loaded(self, history: list):
        """Handle history data loaded from worker"""
        self.update_table(history)
        self.status_label.setText(f"총 {len(history)}건 조회됨")

    def _on_history_error(self, error_message: str):
        """Handle history loading error"""
        logger.error(f"Failed to load history: {error_message}")
        QMessageBox.critical(self, "조회 실패", f"이력 조회에 실패했습니다:\n{error_message}")
        self.status_label.setText("조회 실패")

    def _on_progress_update(self, progress: int):
        """Update progress bar"""
        self.progress_bar.setValue(progress)

    def _on_worker_finished(self):
        """Handle worker completion"""
        self.search_btn.setEnabled(True)
        self.history_table.setSortingEnabled(True)
        self.progress_bar.setVisible(False)
        if self._history_worker:
            self._history_worker.deleteLater()
            self._history_worker = None

    def update_table(self, history: list):
        """테이블 업데이트"""
        self.history_table.setRowCount(len(history))

        for row, item in enumerate(history):
            # 일시
            started_at = item.get('started_at', '')
            if started_at:
                try:
                    # Handle both formats: with and without 'Z'
                    if started_at.endswith('Z'):
                        dt = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                    else:
                        dt = datetime.fromisoformat(started_at)
                    date_str = dt.strftime('%Y-%m-%d %H:%M')
                except (ValueError, AttributeError):
                    date_str = started_at
            else:
                date_str = '-'
            self.history_table.setItem(row, 0, QTableWidgetItem(date_str))

            # LOT 번호 (from nested lot object or lot_id)
            lot = item.get('lot', {})
            if isinstance(lot, dict):
                lot_number = lot.get('lot_number', f"LOT-{item.get('lot_id', '-')}")
            else:
                lot_number = f"LOT-{item.get('lot_id', '-')}"
            self.history_table.setItem(row, 1, QTableWidgetItem(lot_number))

            # Serial 번호
            serial = item.get('serial', {})
            if isinstance(serial, dict):
                serial_number = serial.get('serial_number', '-')
            else:
                serial_number = '-'
            self.history_table.setItem(row, 2, QTableWidgetItem(serial_number))

            # 공정
            process = item.get('process', {})
            if isinstance(process, dict):
                process_name = process.get('process_name_ko', f"공정 {item.get('process_id', '-')}")
            else:
                process_name = f"공정 {item.get('process_id', '-')}"
            self.history_table.setItem(row, 3, QTableWidgetItem(process_name))

            # 작업자
            operator = item.get('operator', {})
            if isinstance(operator, dict):
                operator_name = operator.get('full_name', operator.get('username', '-'))
            else:
                operator_name = '-'
            self.history_table.setItem(row, 4, QTableWidgetItem(operator_name))

            # 소요시간
            duration = item.get('duration_seconds', 0)
            if duration:
                hours = duration // 3600
                minutes = (duration % 3600) // 60
                seconds = duration % 60
                if hours > 0:
                    duration_str = f"{hours}시간 {minutes}분"
                elif minutes > 0:
                    duration_str = f"{minutes}분 {seconds}초"
                else:
                    duration_str = f"{seconds}초"
            else:
                duration_str = '-'
            self.history_table.setItem(row, 5, QTableWidgetItem(duration_str))

            # 결과
            result = item.get('result', '-')
            result_item = QTableWidgetItem(result)
            if result == 'PASS':
                result_item.setForeground(Qt.green)
            elif result == 'FAIL':
                result_item.setForeground(Qt.red)
            elif result == 'REWORK':
                result_item.setForeground(Qt.blue)
            self.history_table.setItem(row, 6, result_item)

            # 측정값 (간략히)
            measurements = item.get('measurements', {})
            if measurements and isinstance(measurements, dict):
                # Show first 2 measurements
                meas_items = list(measurements.items())[:2]
                meas_str = ', '.join([f"{k}: {v}" for k, v in meas_items])
                if len(measurements) > 2:
                    meas_str += f" ... (+{len(measurements)-2})"
            else:
                meas_str = '-'
            self.history_table.setItem(row, 7, QTableWidgetItem(meas_str))

            # 비고
            notes = item.get('notes', '')
            self.history_table.setItem(row, 8, QTableWidgetItem(notes or '-'))

    def export_to_excel(self):
        """Excel로 내보내기 (향후 구현)"""
        QMessageBox.information(
            self,
            "Excel 내보내기",
            "Excel 내보내기 기능은 추후 구현 예정입니다."
        )

    def closeEvent(self, event):
        """Handle dialog close - cleanup worker thread"""
        if self._history_worker and self._history_worker.isRunning():
            logger.info("Cancelling history worker on dialog close...")
            self._history_worker.cancel()
            self._history_worker.quit()
            self._history_worker.wait(1000)  # Wait up to 1 second
            self._history_worker.deleteLater()
            self._history_worker = None
        event.accept()
