"""
Statistics Card Widget.
"""
from PySide6.QtWidgets import QGridLayout
from PySide6.QtCore import Qt
from typing import Dict
from widgets.base_components import InfoCard, StatBadge
from utils.theme_manager import get_theme
import logging

logger = logging.getLogger(__name__)
theme = get_theme()


class StatsCard(InfoCard):
    """Display today's statistics."""

    def __init__(self):
        super().__init__(title="오늘의 통계", min_height=150)
        self.setup_ui()

    def setup_ui(self):
        """Setup UI components."""
        # Stats grid
        grid = QGridLayout()
        grid_spacing = int(theme.get_component_style('statsCard').get('gridSpacing', '15px').replace('px', ''))
        grid.setSpacing(grid_spacing)
        grid.setContentsMargins(0, 0, 0, 0)

        # Get colors from theme
        primary = theme.get_color('primary')
        secondary = theme.get_color('secondary')
        success = theme.get_color('success')
        error = theme.get_color('error')
        warning = theme.get_color('warning')

        # Started
        self.started_badge = StatBadge("착공", "0", primary)
        grid.addWidget(self.started_badge, 0, 0)

        # Completed
        self.completed_badge = StatBadge("완공", "0", secondary)
        grid.addWidget(self.completed_badge, 0, 1)

        # Passed
        self.passed_badge = StatBadge("합격", "0", success)
        grid.addWidget(self.passed_badge, 1, 0)

        # Failed
        self.failed_badge = StatBadge("불량", "0", error)
        grid.addWidget(self.failed_badge, 1, 1)

        # In Progress
        self.in_progress_badge = StatBadge("진행중", "0", warning)
        grid.addWidget(self.in_progress_badge, 2, 0, 1, 2)

        self.content_layout.addLayout(grid)

    def update_stats(self, stats: Dict):
        """
        Update statistics.

        Args:
            stats: Dictionary with stat values
        """
        self.started_badge.update_value(str(stats.get('started', 0)))
        self.completed_badge.update_value(str(stats.get('completed', 0)))
        self.passed_badge.update_value(str(stats.get('passed', 0)))
        self.failed_badge.update_value(str(stats.get('failed', 0)))
        self.in_progress_badge.update_value(str(stats.get('in_progress', 0)))
        logger.debug(f"Stats card updated: {stats}")
