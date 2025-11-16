# JSON Theme System Guide

Complete guide to using JSON-based theming for consistent, customizable UI design.

## Why JSON Themes?

### Problems with Hardcoded Themes
❌ 테마 변경 시 Python 코드 수정 필요  
❌ AI가 색상 값을 직접 수정해야 함  
❌ 여러 테마 관리 어려움  
❌ 실시간 테마 전환 불가능  

### JSON Themes Solution
✅ **선언적**: JSON 파일로 테마 정의  
✅ **유연성**: 런타임에 테마 전환 가능  
✅ **관리 용이**: 파일 하나로 전체 테마 제어  
✅ **AI 친화적**: 구조화된 JSON은 AI가 쉽게 수정  
✅ **변수 참조**: `{colors.primary.main}` 같은 참조 사용  

## Quick Start

### 1. 테마 로드

```python
from ui_components import load_theme

app = QApplication(sys.argv)

# 테마 로드 및 적용
theme = load_theme(app, "default")  # or "dark"
```

### 2. 사용 가능한 테마 확인

```python
from ui_components import list_themes

themes = list_themes()
print(themes)  # ['default', 'dark', ...]
```

### 3. 런타임에 테마 변경

```python
# 다크 테마로 전환
load_theme(app, "dark")

# UI 재생성하면 새 테마 적용됨
```

## JSON 테마 구조

### 기본 구조

```json
{
  "theme": {
    "name": "my-theme",
    "version": "1.0.0",
    "description": "My custom theme"
  },
  
  "colors": {
    "primary": {
      "main": "#3498db",
      "dark": "#2980b9",
      "light": "#5dade2",
      "contrast": "#ffffff"
    }
  },
  
  "typography": {
    "fontFamily": {
      "default": "Arial, sans-serif"
    },
    "fontSize": {
      "normal": 14,
      "large": 18
    }
  },
  
  "spacing": {
    "small": 8,
    "normal": 12,
    "large": 24
  },
  
  "components": {
    "button": {
      "primary": {
        "backgroundColor": "{colors.primary.main}",
        "color": "{colors.primary.contrast}"
      }
    }
  }
}
```

### 변수 참조

테마 내에서 다른 값을 참조할 수 있습니다:

```json
{
  "colors": {
    "primary": {
      "main": "#3498db"
    }
  },
  
  "components": {
    "button": {
      "primary": {
        "backgroundColor": "{colors.primary.main}",
        "hover": {
          "backgroundColor": "{colors.primary.dark}"
        }
      }
    }
  }
}
```

참조는 자동으로 해석됩니다!

## 테마 섹션 상세

### 1. colors

모든 색상 정의:

```json
{
  "colors": {
    "primary": {
      "main": "#3498db",
      "dark": "#2980b9",
      "light": "#5dade2",
      "contrast": "#ffffff"
    },
    "secondary": { /* ... */ },
    "success": { /* ... */ },
    "danger": { /* ... */ },
    "warning": { /* ... */ },
    "info": { /* ... */ },
    "text": {
      "primary": "#2c3e50",
      "secondary": "#7f8c8d",
      "disabled": "#bdc3c7",
      "hint": "#95a5a6"
    },
    "background": {
      "default": "#ecf0f1",
      "paper": "#ffffff",
      "hover": "#f8f9fa"
    },
    "border": {
      "main": "#bdc3c7",
      "dark": "#95a5a6",
      "light": "#ecf0f1"
    }
  }
}
```

### 2. typography

폰트 설정:

```json
{
  "typography": {
    "fontFamily": {
      "default": "Segoe UI, Roboto, Arial, sans-serif",
      "monospace": "Consolas, Monaco, monospace"
    },
    "fontSize": {
      "xxlarge": 28,
      "xlarge": 24,
      "large": 18,
      "normal": 14,
      "small": 12,
      "xsmall": 10
    },
    "fontWeight": {
      "light": 300,
      "normal": 400,
      "medium": 500,
      "semibold": 600,
      "bold": 700
    }
  }
}
```

### 3. spacing

간격 값:

```json
{
  "spacing": {
    "none": 0,
    "xxsmall": 2,
    "xsmall": 4,
    "small": 8,
    "normal": 12,
    "medium": 16,
    "large": 24,
    "xlarge": 32,
    "xxlarge": 48
  }
}
```

### 4. borderRadius

둥근 모서리:

```json
{
  "borderRadius": {
    "none": 0,
    "small": 2,
    "normal": 4,
    "medium": 6,
    "large": 8,
    "xlarge": 12,
    "round": 9999
  }
}
```

### 5. components

컴포넌트별 스타일:

```json
{
  "components": {
    "button": {
      "primary": {
        "backgroundColor": "{colors.primary.main}",
        "color": "{colors.primary.contrast}",
        "border": "none",
        "borderRadius": "{borderRadius.normal}",
        "padding": "{spacing.small} {spacing.medium}",
        "fontSize": "{typography.fontSize.normal}",
        "fontWeight": "{typography.fontWeight.medium}",
        "hover": {
          "backgroundColor": "{colors.primary.dark}"
        },
        "pressed": {
          "backgroundColor": "{colors.primary.dark}"
        },
        "disabled": {
          "backgroundColor": "{colors.border.main}",
          "color": "{colors.text.disabled}"
        }
      }
    }
  }
}
```

## 커스텀 테마 만들기

### 단계별 가이드

**1. 기존 테마 복사**
```bash
cp scripts/ui_components/themes/default.json \
   scripts/ui_components/themes/my-theme.json
```

**2. 테마 정보 수정**
```json
{
  "theme": {
    "name": "my-theme",
    "version": "1.0.0",
    "description": "My custom theme"
  }
}
```

**3. 색상 커스터마이징**
```json
{
  "colors": {
    "primary": {
      "main": "#9C27B0",      // 보라색으로 변경
      "dark": "#7B1FA2",
      "light": "#BA68C8",
      "contrast": "#ffffff"
    }
  }
}
```

**4. 테마 사용**
```python
theme = load_theme(app, "my-theme")
```

### 빠른 색상 변경

primary 색상만 변경하고 싶다면:

```json
{
  "colors": {
    "primary": {
      "main": "#FF5722",     // Orange
      "dark": "#E64A19",
      "light": "#FF7043",
      "contrast": "#ffffff"
    }
  }
}
```

나머지는 그대로 두면 됩니다!

## 실전 예제

### 예제 1: 회사 브랜드 색상 적용

```json
{
  "theme": {
    "name": "company-brand",
    "version": "1.0.0"
  },
  
  "colors": {
    "primary": {
      "main": "#FF6B35",      // 회사 브랜드 오렌지
      "dark": "#E55A2B",
      "light": "#FF8554",
      "contrast": "#ffffff"
    },
    "secondary": {
      "main": "#004E89",      // 회사 브랜드 파랑
      "dark": "#003A66",
      "light": "#1A6BA1",
      "contrast": "#ffffff"
    }
  }
}
```

### 예제 2: 다크 모드

`scripts/ui_components/themes/dark.json` 참고

주요 변경사항:
- 배경: 어두운 색
- 텍스트: 밝은 색
- 색상: 더 밝은 톤

### 예제 3: 미니멀 테마

```json
{
  "colors": {
    "primary": {
      "main": "#000000",      // 검정
      "dark": "#000000",
      "light": "#333333",
      "contrast": "#ffffff"
    },
    "text": {
      "primary": "#000000",
      "secondary": "#666666"
    },
    "background": {
      "default": "#ffffff",
      "paper": "#ffffff"
    },
    "border": {
      "main": "#000000"
    }
  },
  
  "borderRadius": {
    "normal": 0,      // 직각
    "medium": 0
  }
}
```

## AI와 함께 사용하기

### AI에게 테마 수정 요청하기

❌ **나쁜 예:**
```
"테마를 좀 더 밝게 만들어줘"
```

✅ **좋은 예:**
```
"scripts/ui_components/themes/default.json 파일에서
colors.primary.main을 #64b5f6으로 변경해줘"
```

✅ **더 좋은 예:**
```
"scripts/ui_components/themes/ 폴더에 blue-theme.json 파일을 만들어줘:
- colors.primary.main: #2196F3
- colors.secondary.main: #FF9800
- 나머지는 default.json과 동일하게"
```

### 테마 전환 요청

```
"테마 선택 기능을 추가해줘:
- QComboBox로 테마 목록 표시
- 선택 시 load_theme()로 전환
- list_themes()로 사용 가능한 테마 가져오기"
```

## 고급 기능

### 1. 프로그래밍 방식으로 테마 수정

```python
from ui_components import ThemeLoader

# 테마 로드
theme = ThemeLoader.load_theme("default")

# 특정 값 가져오기
primary_color = theme.get("colors.primary.main")
print(f"Primary: {primary_color}")

# 컴포넌트 스타일 가져오기
button_style = theme.get_component_style("button", "primary")
print(button_style)
```

### 2. 런타임 테마 전환

```python
class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_theme = "default"
        self.setup_ui()
    
    def toggle_theme(self):
        """다크/라이트 모드 전환"""
        if self.current_theme == "default":
            self.current_theme = "dark"
        else:
            self.current_theme = "default"
        
        # 테마 전환
        load_theme(QApplication.instance(), self.current_theme)
        
        # UI 재생성
        self.setup_ui()
```

### 3. 커스텀 변수 추가

```json
{
  "custom": {
    "cardShadow": "0 2px 8px rgba(0,0,0,0.1)",
    "animationDuration": 250
  },
  
  "components": {
    "card": {
      "default": {
        "shadow": "{custom.cardShadow}"
      }
    }
  }
}
```

## 트러블슈팅

### 테마가 로드되지 않음
```python
# 사용 가능한 테마 확인
print(list_themes())

# 파일 경로 확인
# scripts/ui_components/themes/your-theme.json
```

### 변수가 해석되지 않음
```json
// ❌ 잘못된 참조
"backgroundColor": "{color.primary}"

// ✅ 올바른 참조
"backgroundColor": "{colors.primary.main}"
```

### 스타일이 적용되지 않음
```python
# 테마를 로드한 후에 컴포넌트 생성
theme = load_theme(app, "default")  # 먼저 로드
button = Button("Text")              # 그 다음 생성
```

## 베스트 프랙티스

1. **의미있는 색상명 사용**
   - `primary`, `secondary` (O)
   - `blue`, `red` (X)

2. **변수 참조 활용**
   - 중복 최소화
   - 일관성 유지

3. **계층적 구조**
   - 색상 → 기본값 정의
   - 컴포넌트 → 색상 참조

4. **테마 버전 관리**
   - version 필드 사용
   - 변경 사항 문서화

5. **테스트**
   - 모든 컴포넌트에서 테마 확인
   - 다크/라이트 모드 모두 테스트

## 요약

JSON 테마 시스템으로:
- ✅ 테마를 코드와 분리
- ✅ AI가 쉽게 수정 가능
- ✅ 런타임 전환 지원
- ✅ 유지보수 용이
- ✅ 확장 가능

**다음 단계:**
1. `json_theme_example.py` 실행해보기
2. `themes/default.json` 수정해보기
3. 커스텀 테마 만들기
4. 앱에 적용하기
