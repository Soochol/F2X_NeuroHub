"""
JSON Theme Loader

Load and apply themes from JSON files.
Supports variable interpolation (e.g., {colors.primary.main})

Usage:
    from ui_components.theme_loader import ThemeLoader
    
    # Load theme
    theme = ThemeLoader.load_theme("default")
    # or
    theme = ThemeLoader.load_theme_from_file("path/to/theme.json")
    
    # Apply to app
    app = QApplication(sys.argv)
    ThemeLoader.apply_theme_to_app(app, theme)
    
    # Use in components
    button_style = theme.get_component_style("button", "primary")
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional


class Theme:
    """Theme data container"""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
        self._resolved_cache = {}
    
    def get(self, path: str, default=None):
        """Get value by dot notation path (e.g., 'colors.primary.main')"""
        keys = path.split('.')
        value = self._data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        # Resolve variables if it's a string
        if isinstance(value, str):
            return self._resolve_variables(value)
        
        return value
    
    def _resolve_variables(self, value: str) -> str:
        """Resolve {variable} references in string"""
        if value in self._resolved_cache:
            return self._resolved_cache[value]
        
        # Find all {variable} patterns
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, value)
        
        result = value
        for match in matches:
            var_value = self.get(match)
            if var_value is not None:
                result = result.replace(f'{{{match}}}', str(var_value))
        
        self._resolved_cache[value] = result
        return result
    
    def get_component_style(self, component: str, variant: str = "default") -> Dict[str, Any]:
        """Get resolved component style"""
        path = f"components.{component}.{variant}"
        style_data = self.get(path, {})
        
        if not style_data:
            return {}
        
        # Recursively resolve all values
        return self._resolve_dict(style_data)
    
    def _resolve_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively resolve all variables in dictionary"""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self._resolve_variables(value)
            elif isinstance(value, dict):
                result[key] = self._resolve_dict(value)
            else:
                result[key] = value
        return result
    
    @property
    def name(self) -> str:
        """Get theme name"""
        return self.get("theme.name", "unknown")
    
    @property
    def colors(self) -> Dict[str, Any]:
        """Get all colors"""
        return self._resolve_dict(self.get("colors", {}))
    
    @property
    def typography(self) -> Dict[str, Any]:
        """Get typography settings"""
        return self._resolve_dict(self.get("typography", {}))
    
    @property
    def spacing(self) -> Dict[str, Any]:
        """Get spacing values"""
        return self.get("spacing", {})
    
    @property
    def border_radius(self) -> Dict[str, Any]:
        """Get border radius values"""
        return self.get("borderRadius", {})


class ThemeLoader:
    """Theme loader and manager"""
    
    _themes_dir = Path(__file__).parent / "themes"
    _current_theme: Optional[Theme] = None
    
    @classmethod
    def load_theme(cls, theme_name: str) -> Theme:
        """Load theme by name from themes directory"""
        theme_file = cls._themes_dir / f"{theme_name}.json"
        
        if not theme_file.exists():
            raise FileNotFoundError(f"Theme '{theme_name}' not found at {theme_file}")
        
        return cls.load_theme_from_file(theme_file)
    
    @classmethod
    def load_theme_from_file(cls, filepath: str) -> Theme:
        """Load theme from JSON file"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Theme file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        theme = Theme(data)
        cls._current_theme = theme
        return theme
    
    @classmethod
    def get_current_theme(cls) -> Optional[Theme]:
        """Get currently loaded theme"""
        return cls._current_theme
    
    @classmethod
    def list_available_themes(cls) -> list:
        """List available theme names"""
        if not cls._themes_dir.exists():
            return []
        
        themes = []
        for file in cls._themes_dir.glob("*.json"):
            themes.append(file.stem)
        
        return sorted(themes)
    
    @classmethod
    def apply_theme_to_app(cls, app, theme: Theme):
        """Apply theme to QApplication"""
        colors = theme.colors
        typography = theme.typography
        
        # Get background colors
        bg_default = colors.get('background', {}).get('default', '#ecf0f1')
        bg_paper = colors.get('background', {}).get('paper', '#ffffff')
        text_primary = colors.get('text', {}).get('primary', '#2c3e50')
        text_contrast = colors.get('primary', {}).get('contrast', '#ffffff')
        border_main = colors.get('border', {}).get('main', '#bdc3c7')
        
        # Get typography
        font_family = typography.get('fontFamily', {}).get('default', 'Arial')
        
        global_style = f"""
            * {{
                font-family: {font_family};
            }}
            
            QWidget {{
                background-color: {bg_default};
                color: {text_primary};
            }}
            
            QMainWindow {{
                background-color: {bg_default};
            }}
            
            QToolTip {{
                background-color: {text_primary};
                color: {text_contrast};
                border: none;
                padding: 4px 8px;
                border-radius: 2px;
            }}
        """
        
        app.setStyleSheet(global_style)
        cls._current_theme = theme
    
    @classmethod
    def generate_qss(cls, component: str, variant: str, theme: Optional[Theme] = None) -> str:
        """Generate QSS stylesheet from theme component definition"""
        if theme is None:
            theme = cls._current_theme
        
        if theme is None:
            raise ValueError("No theme loaded. Call load_theme() first.")
        
        style_data = theme.get_component_style(component, variant)
        
        if not style_data:
            return ""
        
        # Convert style data to QSS
        return cls._dict_to_qss(style_data, component)
    
    @classmethod
    def _dict_to_qss(cls, style_dict: Dict[str, Any], widget_class: str = "QPushButton") -> str:
        """Convert style dictionary to QSS string"""
        qss_parts = []
        
        # Main styles
        main_styles = []
        for key, value in style_dict.items():
            if isinstance(value, dict):
                continue  # Skip nested dicts for now
            
            css_key = cls._camel_to_kebab(key)
            main_styles.append(f"    {css_key}: {value};")
        
        if main_styles:
            qss_parts.append(f"{widget_class} {{\n" + "\n".join(main_styles) + "\n}}")
        
        # Pseudo-states (hover, pressed, disabled, focus)
        pseudo_states = ['hover', 'pressed', 'disabled', 'focus']
        for state in pseudo_states:
            if state in style_dict and isinstance(style_dict[state], dict):
                state_styles = []
                for key, value in style_dict[state].items():
                    css_key = cls._camel_to_kebab(key)
                    state_styles.append(f"    {css_key}: {value};")
                
                if state_styles:
                    qss_parts.append(
                        f"{widget_class}:{state} {{\n" + "\n".join(state_styles) + "\n}}"
                    )
        
        return "\n\n".join(qss_parts)
    
    @staticmethod
    def _camel_to_kebab(name: str) -> str:
        """Convert camelCase to kebab-case"""
        # Handle backgroundColor -> background-color
        result = re.sub('([A-Z])', r'-\1', name).lower()
        return result.lstrip('-')


# Convenience function
def load_and_apply_theme(app, theme_name: str = "default") -> Theme:
    """Load theme and apply to app in one call"""
    theme = ThemeLoader.load_theme(theme_name)
    ThemeLoader.apply_theme_to_app(app, theme)
    return theme


# Example usage
if __name__ == "__main__":
    # List available themes
    print("Available themes:", ThemeLoader.list_available_themes())
    
    # Load theme
    theme = ThemeLoader.load_theme("default")
    
    # Print theme info
    print(f"\nTheme: {theme.name}")
    print(f"Primary color: {theme.get('colors.primary.main')}")
    print(f"Font size: {theme.get('typography.fontSize.normal')}")
    
    # Get component style
    button_style = theme.get_component_style("button", "primary")
    print(f"\nButton primary style:")
    for key, value in button_style.items():
        if not isinstance(value, dict):
            print(f"  {key}: {value}")
    
    # Generate QSS
    qss = ThemeLoader.generate_qss("button", "primary", theme)
    print(f"\nGenerated QSS:")
    print(qss)
