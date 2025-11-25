"""
ViewModel for WIP Dashboard.

Handles WIP statistics retrieval and real-time updates.
"""
import logging
from typing import Dict, List
from PySide6.QtCore import QObject, Signal, QTimer

logger = logging.getLogger(__name__)


class WIPDashboardViewModel(QObject):
    """ViewModel for WIP Dashboard screen."""

    # Signals
    statistics_updated = Signal(dict)   # Statistics data
    error_occurred = Signal(str)        # Error message

    # Refresh interval (milliseconds)
    DEFAULT_REFRESH_INTERVAL = 30000  # 30 seconds

    def __init__(self, api_client, refresh_interval: int = DEFAULT_REFRESH_INTERVAL):
        """
        Initialize WIPDashboardViewModel.

        Args:
            api_client: APIClient instance
            refresh_interval: Auto-refresh interval in milliseconds
        """
        super().__init__()
        self.api_client = api_client
        self.refresh_interval = refresh_interval
        self.current_statistics: Dict = {}

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_statistics)

    def start_auto_refresh(self):
        """Start auto-refresh timer."""
        logger.info(f"Starting auto-refresh (interval: {self.refresh_interval}ms)")
        self.refresh_timer.start(self.refresh_interval)
        # Load initial data
        self.refresh_statistics()

    def stop_auto_refresh(self):
        """Stop auto-refresh timer."""
        logger.info("Stopping auto-refresh")
        self.refresh_timer.stop()

    def set_refresh_interval(self, interval_ms: int):
        """
        Set refresh interval.

        Args:
            interval_ms: Interval in milliseconds
        """
        self.refresh_interval = interval_ms
        if self.refresh_timer.isActive():
            self.refresh_timer.setInterval(interval_ms)
            logger.info(f"Refresh interval updated: {interval_ms}ms")

    def refresh_statistics(self):
        """Refresh WIP statistics."""
        try:
            logger.debug("Refreshing WIP statistics")
            stats = self.api_client.get_wip_statistics()
            self.current_statistics = stats
            self.statistics_updated.emit(stats)
            logger.debug("Statistics updated successfully")

        except Exception as e:
            error_msg = f"통계 조회 실패: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    def get_process_wip_counts(self) -> List[tuple]:
        """
        Get WIP counts by process.

        Returns:
            List of (process_name, count) tuples
        """
        by_process = self.current_statistics.get("by_process", {})
        return [(name, count) for name, count in by_process.items()]

    def get_lot_progress(self) -> List[Dict]:
        """
        Get WIP progress by LOT.

        Returns:
            List of LOT progress dictionaries
        """
        by_lot = self.current_statistics.get("by_lot", [])
        return by_lot

    def get_alerts(self) -> List[Dict]:
        """
        Get problem WIP alerts.

        Returns:
            List of alert dictionaries
        """
        alerts = self.current_statistics.get("alerts", [])
        return alerts

    def get_total_wip(self) -> int:
        """
        Get total WIP count.

        Returns:
            Total WIP count
        """
        return self.current_statistics.get("total_wip", 0)

    def cleanup(self):
        """Clean up resources."""
        self.stop_auto_refresh()
