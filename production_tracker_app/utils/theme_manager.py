"""
Theme Manager - Centralized theme and styling system.

This module provides a centralized way to manage application themes
and styles loaded from JSON configuration.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ThemeManager:
    """Manages application theme loaded from JSON configuration."""

    _instance: Optional['ThemeManager'] = None
    _theme_data: Dict[str, Any] = {}

    def __new__(cls):
        """Singleton pattern to ensure only one theme manager exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize theme manager."""
        if not self._theme_data:
            self.load_theme()

    def load_theme(self, theme_path: Optional[str] = None):
        """
        Load theme from JSON file.

        Args:
            theme_path: Path to theme JSON file. If None, uses default theme.json
        """
        if theme_path is None:
            # Default theme path
            app_dir = Path(__file__).parent.parent
            theme_path = app_dir / "theme.json"
        else:
            theme_path = Path(theme_path)

        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                self._theme_data = json.load(f)
            logger.info(f"Theme loaded: {self._theme_data.get('name', 'Unknown')}")
        except Exception as e:
            logger.error(f"Failed to load theme: {e}")
            self._theme_data = self._get_fallback_theme()

    def _get_fallback_theme(self) -> Dict[str, Any]:
        """Return fallback theme if JSON loading fails."""
        return {
            "colors": {
                "primary": "#3b82f6",
                "background": {"main": "#1a1a1a"},
                "text": {"primary": "#ffffff"}
            }
        }

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get theme value by dot-notation path.

        Args:
            key_path: Dot-separated path to theme value (e.g., 'colors.primary')
            default: Default value if key not found

        Returns:
            Theme value or default

        Example:
            >>> theme = ThemeManager()
            >>> primary_color = theme.get('colors.primary')
            >>> font_size = theme.get('typography.fontSize.base')
        """
        keys = key_path.split('.')
        value = self._theme_data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_color(self, color_key: str) -> str:
        """
        Get color value.

        Args:
            color_key: Color key (e.g., 'primary', 'background.main')

        Returns:
            Color hex string
        """
        return self.get(f'colors.{color_key}', '#ffffff')

    def get_spacing(self, size: str) -> str:
        """
        Get spacing value.

        Args:
            size: Size key (xs, sm, md, lg, xl, xxl)

        Returns:
            Spacing value (e.g., '10px')
        """
        return self.get(f'spacing.{size}', '10px')

    def get_font_size(self, size: str) -> str:
        """
        Get font size.

        Args:
            size: Size key (xs, sm, base, md, lg, xl, xxl)

        Returns:
            Font size (e.g., '14px')
        """
        return self.get(f'typography.fontSize.{size}', '14px')

    def get_border_radius(self, size: str) -> str:
        """
        Get border radius.

        Args:
            size: Size key (sm, md, lg, full)

        Returns:
            Border radius (e.g., '6px')
        """
        return self.get(f'borderRadius.{size}', '4px')

    def get_component_style(self, component_name: str) -> Dict[str, Any]:
        """
        Get complete component style configuration.

        Args:
            component_name: Component name (e.g., 'card', 'button.primary')

        Returns:
            Dictionary of style properties
        """
        return self.get(f'components.{component_name}', {})

    def build_stylesheet(self, style_dict: Dict[str, Any]) -> str:
        """
        Build Qt stylesheet string from style dictionary.

        Args:
            style_dict: Dictionary of CSS properties

        Returns:
            Qt stylesheet string

        Example:
            >>> style = {'fontSize': '14px', 'color': '#ffffff'}
            >>> theme.build_stylesheet(style)
            'font-size: 14px; color: #ffffff;'
        """
        css_rules = []

        for key, value in style_dict.items():
            if isinstance(value, dict):
                # Skip nested dicts (handled separately)
                continue

            # Convert camelCase to kebab-case
            css_key = self._camel_to_kebab(key)
            css_rules.append(f"{css_key}: {value}")

        return '; '.join(css_rules) + ';'

    def _camel_to_kebab(self, text: str) -> str:
        """
        Convert camelCase to kebab-case.

        Args:
            text: camelCase text

        Returns:
            kebab-case text
        """
        result = []
        for i, char in enumerate(text):
            if char.isupper() and i > 0:
                result.append('-')
            result.append(char.lower())
        return ''.join(result)

    def get_card_style(self) -> str:
        """Get default card stylesheet."""
        card_style = self.get_component_style('card')
        return self.build_stylesheet(card_style)

    def get_lot_card_title_style(self) -> str:
        """Get LOT card title stylesheet."""
        style = self.get_component_style('lotCard.title')
        return self.build_stylesheet(style)

    def get_lot_card_lot_label_style(self) -> str:
        """Get LOT card LOT label stylesheet."""
        style = self.get_component_style('lotCard.lotLabel')
        return self.build_stylesheet(style)

    def get_lot_card_info_label_style(self) -> str:
        """Get LOT card info label stylesheet."""
        style = self.get_component_style('lotCard.infoLabel')
        return self.build_stylesheet(style)

    def get_stats_card_title_style(self) -> str:
        """Get stats card title stylesheet."""
        style = self.get_component_style('statsCard.title')
        return self.build_stylesheet(style)

    def get_stats_card_stat_label_style(self, color: str) -> str:
        """
        Get stats card stat label stylesheet.

        Args:
            color: Text color

        Returns:
            Stylesheet string
        """
        style = self.get_component_style('statsCard.statLabel').copy()
        style['color'] = color
        return self.build_stylesheet(style)

    def get_button_style(self, button_type: str = 'primary') -> str:
        """
        Get button stylesheet.

        Args:
            button_type: Button type ('primary', 'secondary')

        Returns:
            Stylesheet string
        """
        style = self.get_component_style(f'button.{button_type}')
        return self.build_stylesheet(style)

    def get_status_label_style(self, color: Optional[str] = None) -> str:
        """
        Get status label stylesheet.

        Args:
            color: Optional text color override

        Returns:
            Stylesheet string
        """
        style = self.get_component_style('statusLabel').copy()
        if color:
            style['color'] = color
        return self.build_stylesheet(style)

    def get_window_background_color(self) -> str:
        """Get main window background color."""
        return self.get('window.backgroundColor', '#1a1a1a')

    def get_window_size(self) -> tuple:
        """Get default window size."""
        width = self.get('window.defaultSize.width', 400)
        height = self.get('window.defaultSize.height', 600)
        return (width, height)

    def get_window_margins(self) -> tuple:
        """Get window content margins."""
        top = self.get('window.contentMargins.top', 15)
        right = self.get('window.contentMargins.right', 15)
        bottom = self.get('window.contentMargins.bottom', 15)
        left = self.get('window.contentMargins.left', 15)
        return (left, top, right, bottom)

    def get_window_spacing(self) -> int:
        """Get window layout spacing."""
        return self.get('window.spacing', 15)


# Global theme instance
_theme = ThemeManager()


def get_theme() -> ThemeManager:
    """
    Get global theme manager instance.

    Returns:
        ThemeManager instance
    """
    return _theme
