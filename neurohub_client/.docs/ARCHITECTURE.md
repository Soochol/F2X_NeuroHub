# Production Tracker App - Architecture Guide

> **Based on PyQt/PySide Skill.md Best Practices**
> JSON-based theme system + Component-driven architecture

## 📐 아키텍처 개요

이 애플리케이션은 **skill.md 권장사항**을 따라 구현되었습니다:
- ✅ **JSON 테마 시스템** - 중앙화된 스타일 관리
- ✅ **컴포넌트 기반 아키텍처** - 재사용 가능한 UI 컴포넌트
- ✅ **MVVM 패턴** - View/ViewModel 분리
- ✅ **Singleton ThemeManager** - 전역 테마 접근

## 🎨 테마 시스템 (Theme System)

### JSON 기반 테마 설정

모든 스타일링은 [`theme.json`](theme.json)에 중앙화되어 있습니다:

```json
{
  "colors": {
    "primary": "#3b82f6",
    "secondary": "#10b981",
    ...
  },
  "typography": {
    "fontSize": {...},
    "fontWeight": {...}
  },
  "components": {
    "card": {...},
    "button": {...}
  }
}
```

### 사용 방법

```python
from utils.theme_manager import get_theme

theme = get_theme()

# 색상 가져오기
primary_color = theme.get_color('primary')

# 컴포넌트 스타일 가져오기
button_style = theme.get_component_style('button.primary')

# 스타일시트 빌드
stylesheet = theme.build_stylesheet(button_style)
```

## 🧱 재사용 가능한 컴포넌트

### 베이스 컴포넌트 ([`base_components.py`](widgets/base_components.py))

모든 UI 컴포넌트는 테마를 사용하는 재사용 가능한 베이스 클래스에서 상속받습니다:

#### `ThemedCard`
```python
card = ThemedCard(min_height=120)
# JSON theme.json의 'components.card' 설정을 자동으로 적용
```

#### `ThemedLabel`
```python
title = ThemedLabel("제목", style_type="title")
info = ThemedLabel("정보", style_type="secondary")
```

#### `ThemedButton`
```python
primary_btn = ThemedButton("확인", button_type="primary")
secondary_btn = ThemedButton("취소", button_type="secondary")
```

#### `StatusIndicator`
```python
status = StatusIndicator("🟢 온라인", status="online")
status.set_status("offline", "🔴 오프라인")
```

#### `InfoCard`
```python
class MyCard(InfoCard):
    def __init__(self):
        super().__init__(title="카드 제목", min_height=150)
        self.setup_ui()

    def setup_ui(self):
        # self.content_layout에 위젯 추가
        label = ThemedLabel("내용")
        self.content_layout.addWidget(label)
```

#### `StatBadge`
```python
badge = StatBadge("착공", "0", "#3b82f6")
badge.update_value("5")  # 값 업데이트
```

## 📁 프로젝트 구조

```
production_tracker_app/
├── theme.json                     # 중앙화된 테마 설정 (JSON)
├── main.py                        # 앱 진입점
├── config.py                      # 설정 관리
│
├── utils/
│   ├── theme_manager.py          # 테마 로드 및 관리
│   ├── logger.py                 # 로깅 유틸리티
│   └── constants.py              # 상수 정의
│
├── widgets/
│   ├── base_components.py        # 재사용 가능한 베이스 컴포넌트
│   ├── lot_display_card.py       # LOT 정보 카드 (InfoCard 상속)
│   └── stats_card.py             # 통계 카드 (InfoCard 상속)
│
├── views/
│   ├── main_window.py            # 메인 윈도우
│   ├── login_dialog.py           # 로그인 대화상자
│   └── settings_dialog.py        # 설정 대화상자
│
├── services/                      # 비즈니스 로직 서비스
└── viewmodels/                    # MVVM 뷰모델
```

## 🔄 데이터 흐름

```
JSON Theme File (theme.json)
    ↓
ThemeManager (Singleton)
    ↓
Base Components (ThemedCard, ThemedLabel, etc.)
    ↓
Custom Widgets (LotDisplayCard, StatsCard)
    ↓
Views (MainWindow)
```

## ✅ 테마 시스템의 장점

1. **중앙화된 스타일 관리**
   - 모든 스타일이 `theme.json`에 정의
   - 색상, 폰트, 간격 등을 한 곳에서 수정

2. **재사용 가능한 컴포넌트**
   - `base_components.py`의 컴포넌트를 프로젝트 전체에서 재사용
   - 일관된 UI/UX 보장

3. **유지보수 용이성**
   - 스타일 변경 시 JSON만 수정
   - 코드 중복 제거

4. **확장성**
   - 새로운 컴포넌트 추가 용이
   - 테마 전환 기능 쉽게 구현 가능 (light/dark mode)

## 🎯 새 컴포넌트 추가하기

### 1. JSON에 스타일 정의

`theme.json`에 새 컴포넌트 스타일 추가:

```json
{
  "components": {
    "myComponent": {
      "backgroundColor": "#2a2a2a",
      "fontSize": "14px",
      "padding": "10px"
    }
  }
}
```

### 2. 베이스 컴포넌트 사용

```python
from widgets.base_components import ThemedCard, ThemedLabel
from utils.theme_manager import get_theme

class MyComponent(ThemedCard):
    def __init__(self):
        super().__init__(min_height=100)
        self.setup_ui()

    def setup_ui(self):
        theme = get_theme()
        layout = QVBoxLayout(self)

        # 테마에서 스타일 가져오기
        style = theme.get_component_style('myComponent')

        label = ThemedLabel("내용", style_type="base")
        layout.addWidget(label)
```

## 🔧 ThemeManager API

### 기본 메서드

- `get(key_path, default)` - dot-notation으로 값 가져오기
- `get_color(color_key)` - 색상 값 가져오기
- `get_spacing(size)` - 간격 값 가져오기
- `get_font_size(size)` - 폰트 크기 가져오기
- `get_border_radius(size)` - 테두리 반경 가져오기

### 컴포넌트 메서드

- `get_component_style(component_name)` - 컴포넌트 스타일 딕셔너리
- `build_stylesheet(style_dict)` - Qt 스타일시트 문자열 생성

### 전용 메서드

- `get_card_style()` - 카드 스타일시트
- `get_button_style(button_type)` - 버튼 스타일시트
- `get_window_size()` - 윈도우 크기
- `get_window_margins()` - 윈도우 여백
- `get_window_spacing()` - 윈도우 간격

## 🎨 테마 커스터마이징

### 색상 변경

`theme.json`에서 색상 수정:

```json
{
  "colors": {
    "primary": "#ff6b6b",  // 빨간색으로 변경
    "secondary": "#4ecdc4"
  }
}
```

### 새 컴포넌트 스타일 추가

```json
{
  "components": {
    "notification": {
      "backgroundColor": "#fef3c7",
      "borderColor": "#f59e0b",
      "borderRadius": "8px",
      "padding": "12px",
      "fontSize": "14px"
    }
  }
}
```

### 폰트 크기 조정

```json
{
  "typography": {
    "fontSize": {
      "base": "14px",  // 기본 폰트 크기
      "lg": "18px",    // 큰 폰트
      "xl": "22px"     // 매우 큰 폰트
    }
  }
}
```

## 🚀 모범 사례 (skill.md 기준)

### 1. 테마 로드 순서 (CRITICAL)
```python
# ✅ Correct order (skill.md recommended)
app = QApplication(sys.argv)
theme = get_theme()  # Load theme FIRST
window = MainWindow(viewmodel, config)
window.show()

# ❌ Wrong order - theme won't apply properly
app = QApplication(sys.argv)
window = MainWindow()  # Too early!
theme = get_theme()
```

### 2. 스타일은 항상 JSON에 정의
```python
# ❌ Hard-coded colors in code
label.setStyleSheet("color: #ffffff")

# ✅ Use JSON theme system
# Edit theme.json: "colors": { "text": { "primary": "#ededed" } }
label = ThemedLabel("text", style_type="primary")
```

### 3. 컴포넌트 우선 사용
```python
# ❌ Don't create widgets directly
button = QPushButton("Click")
button.setStyleSheet("background: #3498db")  # Hard to maintain

# ✅ Use themed components
button = ThemedButton("Click", button_type="primary")  # Auto-themed
```

### 4. 일관된 네이밍
- JSON keys: camelCase (`fontSize`, `backgroundColor`)
- Python: snake_case (`get_font_size`, `theme_manager`)

### 5. Singleton 테마 매니저
```python
from utils.theme_manager import get_theme
theme = get_theme()  # Always returns same instance
```

## 📚 참고 자료

- [theme.json](theme.json) - 테마 설정 파일
- [theme_manager.py](utils/theme_manager.py) - 테마 매니저 구현
- [base_components.py](widgets/base_components.py) - 재사용 가능한 컴포넌트
- [lot_display_card.py](widgets/lot_display_card.py) - 사용 예시
- [stats_card.py](widgets/stats_card.py) - 사용 예시
