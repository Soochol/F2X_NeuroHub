"""
Theme Manager - Centralized theme and styling system with QSS generation.

Provides JSON-based theming with Property Variant pattern support.
Single source of truth for all application styling.
"""
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, Optional

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor

logger = logging.getLogger(__name__)


class ThemeManager:
    """Manages application theme loaded from JSON configuration."""

    _instance: Optional['ThemeManager'] = None
    _theme_data: Dict[str, Any] = {}
    _resolved_cache: Dict[str, str] = {}

    def __new__(cls) -> 'ThemeManager':
        """Singleton pattern to ensure only one theme manager exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize theme manager."""
        pass

    def load_theme(self, theme_name: str) -> 'ThemeManager':
        """
        Load theme from JSON file.

        Args:
            theme_name: Theme name (e.g., "production_tracker")

        Returns:
            ThemeManager instance for chaining
        """
        theme_dir = Path(__file__).parent.parent / "themes"
        theme_path = theme_dir / f"{theme_name}.json"

        if not theme_path.exists():
            logger.error("Theme file not found: %s", theme_path)
            self._theme_data = self._get_fallback_theme()
            return self

        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                self._theme_data = json.load(f)
            self._resolved_cache = {}
            loaded_name = self._theme_data.get('theme_name', theme_name)
            logger.info("Theme loaded: %s", loaded_name)
        except (OSError, json.JSONDecodeError) as e:
            logger.error("Failed to load theme: %s", e)
            self._theme_data = self._get_fallback_theme()

        return self

    def _get_fallback_theme(self) -> Dict[str, Any]:
        """Return fallback theme if JSON loading fails."""
        return {
            "colors": {
                "brand": {"main": "#3ECF8E"},
                "primary": {"main": "#3ECF8E"},
                "background": {"default": "#0f0f0f", "elevated": "#1f1f1f"},
                "text": {"primary": "#ededed", "secondary": "#a8a8a8"},
                "border": {"default": "#1a1a1a"}
            },
            "typography": {
                "size": {"title": 18, "body": 14, "caption": 12}
            },
            "spacing": {"sm": 8, "md": 16, "lg": 24},
            "radius": {"sm": 4, "md": 8, "lg": 16}
        }

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get theme value by dot-notation path with variable resolution.

        Args:
            key_path: Dot-separated path (e.g., 'colors.primary.main')
            default: Default value if key not found

        Returns:
            Theme value with variables resolved
        """
        keys = key_path.split('.')
        value = self._theme_data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        if isinstance(value, str):
            return self._resolve_variables(value)

        return value

    def _resolve_variables(self, value: str) -> str:
        """
        Resolve variable references: {variable} -> actual value.

        Example: "{colors.primary.main}" -> "#3ECF8E"
        """
        if value in self._resolved_cache:
            return self._resolved_cache[value]

        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, value)

        result = value
        for match in matches:
            var_value = self.get(match)
            if var_value is not None:
                result = result.replace(f'{{{match}}}', str(var_value))

        self._resolved_cache[value] = result
        return result

    def get_component_style(self, component_path: str) -> Dict[str, Any]:
        """
        Get component style dictionary with variables resolved.

        Args:
            component_path: Path like "button.primary" or "card.default"

        Returns:
            Dictionary of resolved style properties
        """
        style = self.get(f'components.{component_path}', {})

        if not isinstance(style, dict):
            return {}

        resolved = {}
        for key, value in style.items():
            if isinstance(value, str):
                resolved[key] = self._resolve_variables(value)
            else:
                resolved[key] = value

        return resolved

    def generate_qss(self) -> str:
        """
        Generate complete QSS stylesheet from theme with Property Variant support.

        Returns:
            Complete QSS stylesheet string
        """
        colors = self._theme_data.get('colors', {})
        typography = self._theme_data.get('typography', {})
        spacing = self._theme_data.get('spacing', {})
        radius = self._theme_data.get('radius', {})
        components = self._theme_data.get('components', {})

        # Resolve all values
        bg_default = self.get('colors.background.default', '#0f0f0f')
        bg_elevated = self.get('colors.background.elevated', '#1f1f1f')
        bg_hover = self.get('colors.background.hover', '#252525')

        text_primary = self.get('colors.text.primary', '#ededed')
        text_secondary = self.get('colors.text.secondary', '#a8a8a8')
        text_on_brand = self.get('colors.text.onBrand', '#000000')

        border_default = self.get('colors.border.default', '#1a1a1a')
        border_light = self.get('colors.border.light', '#2a2a2a')

        brand_main = self.get('colors.brand.main', '#3ECF8E')
        brand_dark = self.get('colors.brand.dark', '#2FB574')

        primary_main = self.get('colors.primary.main', '#3ECF8E')
        primary_dark = self.get('colors.primary.dark', '#2FB574')

        danger_main = self.get('colors.danger.main', '#F04438')
        danger_dark = self.get('colors.danger.dark', '#D92D20')

        success_main = self.get('colors.success.main', '#3ECF8E')
        warning_main = self.get('colors.warning.main', '#F97316')

        font_family = self.get('typography.fontFamily.primary', 'sans-serif')
        font_title = self.get('typography.size.title', 18)
        font_body = self.get('typography.size.body', 14)
        font_caption = self.get('typography.size.caption', 12)

        radius_sm = self.get('radius.sm', 4)
        radius_md = self.get('radius.md', 8)
        radius_lg = self.get('radius.lg', 16)

        spacing_sm = self.get('spacing.sm', 8)
        spacing_md = self.get('spacing.md', 16)
        spacing_lg = self.get('spacing.lg', 24)

        qss = f"""
/* ========== Global Styles ========== */
QMainWindow, QDialog {{
    background-color: {bg_default};
    color: {text_primary};
    font-family: {font_family};
    font-size: {font_body}px;
}}

QWidget {{
    color: {text_primary};
    font-family: {font_family};
}}

/* ========== QLabel Variants ========== */
QLabel {{
    color: {text_primary};
    font-size: {font_body}px;
}}

QLabel[variant="title"] {{
    font-size: {font_title}px;
    font-weight: bold;
    color: {text_primary};
}}

QLabel[variant="body"] {{
    font-size: {font_body}px;
    color: {text_primary};
}}

QLabel[variant="caption"] {{
    font-size: {font_caption}px;
    color: {text_secondary};
}}

QLabel[variant="success"] {{
    color: {success_main};
    font-weight: 500;
}}

QLabel[variant="danger"] {{
    color: {danger_main};
    font-weight: 500;
}}

QLabel[variant="warning"] {{
    color: {warning_main};
    font-weight: 500;
}}

QLabel[variant="brand"] {{
    color: {brand_main};
    font-weight: bold;
}}

/* ========== QPushButton Variants ========== */
QPushButton {{
    background-color: {bg_elevated};
    color: {text_primary};
    border: 1px solid {border_default};
    border-radius: {radius_md}px;
    padding: {spacing_sm}px {spacing_md}px;
    font-size: {font_body}px;
    font-weight: 500;
    min-height: 32px;
}}

QPushButton:hover {{
    background-color: {bg_hover};
    border-color: {border_light};
}}

QPushButton:pressed {{
    background-color: {border_default};
}}

QPushButton:disabled {{
    background-color: {border_default};
    color: {text_secondary};
}}

QPushButton[variant="primary"] {{
    background-color: {primary_main};
    color: {text_on_brand};
    border: none;
    font-weight: bold;
}}

QPushButton[variant="primary"]:hover {{
    background-color: {primary_dark};
}}

QPushButton[variant="primary"]:pressed {{
    background-color: {brand_dark};
}}

QPushButton[variant="danger"] {{
    background-color: {danger_main};
    color: #ffffff;
    border: none;
    font-weight: bold;
}}

QPushButton[variant="danger"]:hover {{
    background-color: {danger_dark};
}}

QPushButton[variant="secondary"] {{
    background-color: transparent;
    color: {text_primary};
    border: 1px solid {border_default};
}}

QPushButton[variant="secondary"]:hover {{
    background-color: {bg_elevated};
}}

QPushButton[variant="ghost"] {{
    background-color: transparent;
    border: none;
    color: {text_secondary};
}}

QPushButton[variant="ghost"]:hover {{
    background-color: {bg_elevated};
    color: {text_primary};
}}

/* ========== QFrame Card Variants ========== */
QFrame[variant="card"] {{
    background-color: {bg_default};
    border: 1px solid {border_default};
    border-radius: {radius_lg}px;
}}

QFrame[variant="elevated"] {{
    background-color: {bg_elevated};
    border: 1px solid {border_default};
    border-radius: {radius_lg}px;
}}

/* ========== QLineEdit ========== */
QLineEdit {{
    background-color: {bg_elevated};
    color: {text_primary};
    border: 1px solid {border_default};
    border-radius: {radius_md}px;
    padding: {spacing_sm}px {spacing_md}px;
    font-size: {font_body}px;
    min-height: 36px;
}}

QLineEdit:focus {{
    border-color: {brand_main};
}}

QLineEdit:disabled {{
    background-color: {border_default};
    color: {text_secondary};
}}

/* ========== QComboBox ========== */
QComboBox {{
    background-color: {bg_elevated};
    color: {text_primary};
    border: 1px solid {border_default};
    border-radius: {radius_md}px;
    padding: {spacing_sm}px {spacing_md}px;
    font-size: {font_body}px;
    min-height: 36px;
}}

QComboBox:hover {{
    border-color: {border_light};
}}

QComboBox:focus {{
    border-color: {brand_main};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {bg_elevated};
    color: {text_primary};
    border: 1px solid {border_default};
    selection-background-color: {brand_main};
    selection-color: {text_on_brand};
}}

/* ========== QScrollArea ========== */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    background-color: {bg_default};
    width: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background-color: {border_default};
    border-radius: 4px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {border_light};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {bg_default};
    height: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal {{
    background-color: {border_default};
    border-radius: 4px;
    min-width: 20px;
}}

/* ========== QGroupBox ========== */
QGroupBox {{
    font-weight: bold;
    border: 1px solid {border_default};
    border-radius: {radius_lg}px;
    margin-top: 16px;
    padding: 16px;
    padding-top: 28px;
    color: {text_primary};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 12px;
    background-color: {bg_elevated};
    border-radius: {radius_md}px;
    color: {brand_main};
}}

/* ========== QCheckBox ========== */
QCheckBox {{
    color: {text_primary};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {border_default};
    border-radius: {radius_sm}px;
    background-color: {bg_elevated};
}}

QCheckBox::indicator:checked {{
    background-color: {brand_main};
    border-color: {brand_main};
}}

/* ========== QRadioButton ========== */
QRadioButton {{
    color: {text_primary};
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {border_default};
    border-radius: 9px;
    background-color: {bg_elevated};
}}

QRadioButton::indicator:checked {{
    background-color: {brand_main};
    border-color: {brand_main};
}}

/* ========== QTabWidget ========== */
QTabWidget::pane {{
    border: 1px solid {border_default};
    border-radius: {radius_md}px;
    background-color: {bg_default};
}}

QTabBar::tab {{
    background-color: {bg_elevated};
    color: {text_secondary};
    padding: {spacing_sm}px {spacing_md}px;
    border: 1px solid {border_default};
    border-bottom: none;
    border-top-left-radius: {radius_md}px;
    border-top-right-radius: {radius_md}px;
}}

QTabBar::tab:selected {{
    background-color: {bg_default};
    color: {text_primary};
}}

QTabBar::tab:hover:!selected {{
    background-color: {bg_hover};
}}

/* ========== QProgressBar ========== */
QProgressBar {{
    background-color: {bg_elevated};
    border: 1px solid {border_default};
    border-radius: {radius_sm}px;
    text-align: center;
    color: {text_primary};
    height: 20px;
}}

QProgressBar::chunk {{
    background-color: {brand_main};
    border-radius: {radius_sm}px;
}}

/* ========== QSlider ========== */
QSlider::groove:horizontal {{
    height: 4px;
    background-color: {border_default};
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background-color: {brand_main};
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}

QSlider::sub-page:horizontal {{
    background-color: {brand_main};
    border-radius: 2px;
}}

/* ========== QToolTip ========== */
QToolTip {{
    background-color: {bg_elevated};
    color: {text_primary};
    border: 1px solid {border_default};
    border-radius: {radius_sm}px;
    padding: 4px 8px;
}}

/* ========== QMenu ========== */
QMenu {{
    background-color: {bg_elevated};
    color: {text_primary};
    border: 1px solid {border_default};
    border-radius: {radius_md}px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px;
    border-radius: {radius_sm}px;
}}

QMenu::item:selected {{
    background-color: {brand_main};
    color: {text_on_brand};
}}

QMenu::separator {{
    height: 1px;
    background-color: {border_default};
    margin: 4px 8px;
}}

/* ========== QStatusBar ========== */
QStatusBar {{
    background-color: {bg_default};
    color: {text_secondary};
    font-size: {font_caption}px;
    border-top: 1px solid {border_default};
}}

QStatusBar::item {{
    border: none;
}}

/* ========== Toast Notification ========== */
QFrame[variant="toast"] {{
    background-color: {bg_elevated};
    color: {text_primary};
    border: 1px solid {border_default};
    border-radius: {radius_md}px;
    padding: 12px 16px;
}}

QFrame[variant="toast-success"] {{
    background-color: {success_main};
    color: #ffffff;
    border: none;
    border-radius: {radius_md}px;
    padding: 12px 16px;
}}

QFrame[variant="toast-danger"] {{
    background-color: {danger_main};
    color: #ffffff;
    border: none;
    border-radius: {radius_md}px;
    padding: 12px 16px;
}}

QFrame[variant="toast-warning"] {{
    background-color: {warning_main};
    color: #000000;
    border: none;
    border-radius: {radius_md}px;
    padding: 12px 16px;
}}

QFrame[variant="toast-info"] {{
    background-color: {brand_main};
    color: #000000;
    border: none;
    border-radius: {radius_md}px;
    padding: 12px 16px;
}}
"""
        return qss

    def get_qt_color(self, key_path: str, default: str = "#000000") -> QColor:
        """
        Get theme color as QColor object.

        Args:
            key_path: Dot-separated path (e.g., 'colors.semantic.success')
            default: Default color hex if key not found

        Returns:
            QColor object
        """
        color_hex = self.get(key_path, default)
        return QColor(color_hex)

    def apply_to_app(self, app: QApplication) -> None:
        """
        Apply generated QSS to the application.

        Args:
            app: QApplication instance
        """
        qss = self.generate_qss()
        app.setStyleSheet(qss)
        logger.info("Theme QSS applied to application")


# Global theme instance
_theme_manager = ThemeManager()


def load_theme(app: QApplication, theme_name: str) -> ThemeManager:
    """
    Load theme and apply to application.

    Args:
        app: QApplication instance
        theme_name: Theme name (e.g., "production_tracker")

    Returns:
        ThemeManager instance
    """
    _theme_manager.load_theme(theme_name)
    _theme_manager.apply_to_app(app)
    return _theme_manager


def get_theme() -> ThemeManager:
    """
    Get global theme manager instance.

    Returns:
        ThemeManager instance
    """
    return _theme_manager
