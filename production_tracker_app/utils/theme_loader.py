"""Production Tracker - Theme Loader

JSON 기반 테마 시스템:
- 변수 참조 자동 해결: {colors.primary.main} → #3ECF8E
- 컴포넌트 스타일 자동 적용
- globalStyles → QSS 변환
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
        예: "{colors.primary.main}" → "#3ECF8E"
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

    def get_component_style(self, component_type: str, variant: str = "default") -> Dict[str, Any]:
        """
        컴포넌트 스타일을 딕셔너리로 반환

        Args:
            component_type: 컴포넌트 타입 (예: "statusBar", "statusLabel")
            variant: 변형 (예: "default", "success", "danger")

        Returns:
            스타일 딕셔너리 (변수 해결됨)
        """
        component_path = f"components.{component_type}.{variant}"
        component_styles = self.get(component_path, {})

        if not isinstance(component_styles, dict):
            return {}

        resolved_styles = {}
        for key, value in component_styles.items():
            if isinstance(value, str):
                resolved_styles[key] = self._resolve_variables(value)
            else:
                resolved_styles[key] = value

        return resolved_styles

    def to_qss(self) -> str:
        """
        globalStyles를 QSS 문자열로 변환

        Returns:
            QSS 스타일시트 문자열
        """
        global_styles = self._data.get("globalStyles", {})
        qss_parts = []

        for selector, properties in global_styles.items():
            if not isinstance(properties, dict):
                continue

            resolved_props = []
            for prop, value in properties.items():
                if isinstance(value, str):
                    resolved_value = self._resolve_variables(value)
                else:
                    resolved_value = str(value)
                resolved_props.append(f"    {prop}: {resolved_value};")

            if resolved_props:
                qss_parts.append(f"{selector} {{\n" + "\n".join(resolved_props) + "\n}")

        return "\n\n".join(qss_parts)

    def component_to_qss(self, style: Dict[str, Any]) -> str:
        """
        컴포넌트 스타일 딕셔너리를 QSS 문자열로 변환

        Args:
            style: get_component_style()로 가져온 스타일 딕셔너리

        Returns:
            QSS 스타일 문자열 (선택자 없이)
        """
        qss_props = []

        # camelCase를 kebab-case로 변환하는 매핑
        prop_mapping = {
            "backgroundColor": "background-color",
            "fontSize": "font-size",
            "fontWeight": "font-weight",
            "fontFamily": "font-family",
            "borderRadius": "border-radius",
            "boxShadow": "box-shadow",
            "hoverBackground": None,  # QSS에서 직접 지원 안 함
            "pressedBackground": None,
        }

        for key, value in style.items():
            # 매핑에 있으면 변환, 없으면 원본 사용
            css_prop = prop_mapping.get(key, key)

            if css_prop is None:  # 지원 안 되는 속성 스킵
                continue

            # 숫자 값에 px 추가 (폰트 크기, 패딩 등)
            if isinstance(value, (int, float)) and key in ("fontSize", "padding", "borderRadius"):
                value = f"{value}px"

            qss_props.append(f"{css_prop}: {value};")

        return " ".join(qss_props)

    def get_all(self) -> Dict[str, Any]:
        """전체 테마 데이터 반환"""
        return self._data


class ThemeLoader:
    """테마 로더 - JSON 파일 로드"""

    _current_theme: Optional[Theme] = None

    @staticmethod
    def load_theme(theme_name: str) -> Theme:
        """
        테마 JSON 파일 로드

        Args:
            theme_name: 테마 이름 (예: "production_tracker")

        Returns:
            Theme 객체
        """
        # production_tracker_app/themes/ 디렉토리에서 테마 파일 찾기
        theme_dir = Path(__file__).parent.parent / "themes"
        theme_file = theme_dir / f"{theme_name}.json"

        if not theme_file.exists():
            raise FileNotFoundError(f"테마 파일을 찾을 수 없습니다: {theme_file}")

        with open(theme_file, "r", encoding="utf-8") as f:
            theme_data = json.load(f)

        theme = Theme(theme_data)
        ThemeLoader._current_theme = theme
        return theme

    @staticmethod
    def get_current_theme() -> Optional[Theme]:
        """현재 로드된 테마 반환"""
        return ThemeLoader._current_theme


def get_current_theme() -> Optional[Theme]:
    """현재 로드된 테마 반환 (간편 함수)"""
    return ThemeLoader.get_current_theme()
