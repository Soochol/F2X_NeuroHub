"""F2X NeuroHub MES - Theme Loader

JSON 기반 테마 시스템:
- 변수 참조 자동 해결: {colors.primary.main} → #1976d2
- QSS 스타일시트 자동 생성
- 글로벌 테마 적용
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional


class Theme:
    """테마 데이터 및 변수 해결"""

    def __init__(self, theme_data: Dict[str, Any]):
        self._data = theme_data
        self._resolved_cache: Dict[str, str] = {}

    def get(self, path: str, default: Any = None) -> Any:
        """
        점 표기법으로 중첩된 값 가져오기
        예: "colors.primary.main" → theme_data["colors"]["primary"]["main"]
        """
        keys = path.split(".")
        value = self._data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        # 문자열이면 변수 참조 해결
        if isinstance(value, str):
            return self._resolve_variables(value)

        return value

    def _resolve_variables(self, value: str) -> str:
        """
        변수 참조 해결: {variable} → 실제 값
        예: "{colors.primary.main}" → "#1976d2"
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

    def get_all(self) -> Dict[str, Any]:
        """전체 테마 데이터 반환"""
        return self._data


class ThemeLoader:
    """테마 로더 - JSON 파일 로드 및 QSS 생성"""

    _current_theme: Optional[Theme] = None

    @staticmethod
    def load_theme(theme_name: str) -> Theme:
        """
        테마 JSON 파일 로드

        Args:
            theme_name: 테마 이름 (예: "neurohub")

        Returns:
            Theme 객체
        """
        theme_dir = Path(__file__).parent / "themes"
        theme_file = theme_dir / f"{theme_name}.json"

        if not theme_file.exists():
            raise FileNotFoundError(f"테마 파일을 찾을 수 없습니다: {theme_file}")

        with open(theme_file, "r", encoding="utf-8") as f:
            theme_data = json.load(f)

        theme = Theme(theme_data)
        ThemeLoader._current_theme = theme
        return theme

    @staticmethod
    def generate_global_qss(theme: Theme) -> str:
        """
        글로벌 QSS 스타일시트 생성

        Args:
            theme: Theme 객체

        Returns:
            QSS 스타일시트 문자열
        """
        global_styles = theme.get("globalStyles", {})
        qss_parts = []

        for selector, properties in global_styles.items():
            qss_parts.append(f"{selector} {{")
            for prop, value in properties.items():
                # 변수 참조 해결
                resolved_value = theme.get(value) if isinstance(value, str) and value.startswith("{") else value
                qss_parts.append(f"    {prop}: {resolved_value};")
            qss_parts.append("}")

        return "\n".join(qss_parts)

    @staticmethod
    def generate_component_qss(
        component_type: str,
        variant: str,
        theme: Theme,
        extra_states: Optional[Dict[str, str]] = None
    ) -> str:
        """
        컴포넌트별 QSS 스타일시트 생성

        Args:
            component_type: 컴포넌트 타입 (예: "button", "statCard")
            variant: 변형 (예: "primary", "success")
            theme: Theme 객체
            extra_states: 추가 상태 스타일 (예: {"hover": {...}, "pressed": {...}})

        Returns:
            QSS 스타일시트 문자열
        """
        component_path = f"components.{component_type}.{variant}"
        component_styles = theme.get(component_path, {})

        if not component_styles:
            return ""

        qss_parts = []

        # 기본 스타일
        for prop, value in component_styles.items():
            if prop.startswith("hover") or prop.startswith("pressed"):
                continue  # 상태 스타일은 나중에 처리

            css_prop = _to_css_property(prop)
            resolved_value = theme.get(value) if isinstance(value, str) and value.startswith("{") else value
            qss_parts.append(f"{css_prop}: {resolved_value};")

        # hover 스타일
        if "hoverBackground" in component_styles:
            hover_bg = theme.get(component_styles["hoverBackground"]) \
                if component_styles["hoverBackground"].startswith("{") \
                else component_styles["hoverBackground"]
            # hover는 별도로 반환하지 않고, 컴포넌트에서 직접 처리

        return "\n".join(qss_parts)

    @staticmethod
    def get_component_style_dict(
        component_type: str,
        variant: str,
        theme: Theme
    ) -> Dict[str, Any]:
        """
        컴포넌트 스타일을 딕셔너리로 반환 (Python 코드에서 직접 사용)

        Args:
            component_type: 컴포넌트 타입
            variant: 변형
            theme: Theme 객체

        Returns:
            스타일 딕셔너리 (변수 해결됨)
        """
        component_path = f"components.{component_type}.{variant}"
        component_styles = theme.get(component_path, {})

        resolved_styles = {}
        for key, value in component_styles.items():
            if isinstance(value, str) and value.startswith("{"):
                resolved_styles[key] = theme.get(value)
            else:
                resolved_styles[key] = value

        return resolved_styles


def _to_css_property(prop: str) -> str:
    """
    camelCase → kebab-case 변환
    예: "backgroundColor" → "background-color"
    """
    result = []
    for i, char in enumerate(prop):
        if char.isupper() and i > 0:
            result.append('-')
            result.append(char.lower())
        else:
            result.append(char.lower())
    return ''.join(result)


def load_and_apply_theme(app, theme_name: str = "neurohub") -> Theme:
    """
    테마 로드 및 QApplication에 글로벌 스타일 적용

    Args:
        app: QApplication 인스턴스
        theme_name: 테마 이름

    Returns:
        Theme 객체
    """
    theme = ThemeLoader.load_theme(theme_name)
    global_qss = ThemeLoader.generate_global_qss(theme)
    app.setStyleSheet(global_qss)
    return theme


def get_current_theme() -> Optional[Theme]:
    """현재 로드된 테마 반환"""
    return ThemeLoader._current_theme
