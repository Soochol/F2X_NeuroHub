# GUI Debugging Tools - 종합 가이드

## 개요

PySide6/PyQt6 GUI 개발을 위한 3가지 강력한 디버깅 도구:

1. **Visual Debugger** (동적 분석) - 실행 중인 앱 분석
2. **GUI Code Analyzer** (정적 분석) - 코드 파일 분석
3. **Hot Reload** (개발 도구) - 파일 변경 시 자동 재시작

## 도구 비교표

| 특성 | Visual Debugger | GUI Analyzer | Hot Reload |
|------|----------------|--------------|------------|
| **분석 시점** | 앱 실행 중 | 코드 작성 후 | 개발 중 |
| **실행 필요** | ✅ 필요 | ❌ 불필요 | ✅ 앱 실행 |
| **위젯 감지** | 모든 동적 위젯 | AST 기반 파싱 | - |
| **실제 크기** | 렌더링 크기 | 코드 추정 | - |
| **겹침 감지** | 시각적 | 좌표 계산 | - |
| **리포트** | 실시간 | HTML 저장 | 콘솔 로그 |
| **Best Practices** | ❌ | ✅ | - |
| **생산성** | 디버깅 | 코드 품질 | 🚀 극대화 |

## 1. Visual Debugger - 실시간 분석

### 목적
실행 중인 앱의 위젯을 실시간으로 분석

### 사용 시기
- 레이아웃이 예상과 다를 때
- 위젯이 보이지 않을 때
- 스타일시트 문제 디버깅
- 위젯 크기/위치 확인

### 사용 방법
```python
from visual_debugger import launch_with_debugger

app = QApplication(sys.argv)
window = MainWindow()
debugger = launch_with_debugger(window)  # 디버거 실행
sys.exit(app.exec())
```

### 제공 기능
- 📂 **Widget Tree**: 계층 구조 시각화
- 🔧 **Properties Inspector**: Geometry, visibility, parent
- 🎨 **Stylesheet Viewer**: 적용된 스타일 확인
- ⚠️ **Issue Detection**: 작은 크기, 부모 없음 감지
- ✨ **Visual Highlight**: 선택한 위젯 하이라이트
- 🖼️ **Show All Borders**: 모든 위젯 테두리 표시

### 장점
✅ 실제 렌더링 결과 확인
✅ 동적 생성 위젯 모두 감지
✅ 실시간 인터랙션
✅ 시각적 하이라이트

### 단점
❌ 앱 실행 필요
❌ 리포트 저장 안됨
❌ Best practices 검증 없음

---

## 2. GUI Code Analyzer - 정적 분석

### 목적
UI 코드 파일을 분석하여 종합 리포트 생성

### 사용 시기
- 코드 리뷰 전
- PR 제출 전
- 리팩토링 후
- 문서화 필요 시
- CI/CD 파이프라인

### 사용 방법
```bash
cd .claude/skills/pyqt-pyside-gui/tools
python gui_analyzer.py path/to/ui_file.py
```

### 제공 기능
- 🌳 **Widget Tree 자동 생성**: AST 기반 위젯 추출
- 🔍 **Property 분석**: Geometry, visibility, styling
- ⚠️ **이슈 감지**:
  - Size issues (너무 작은 위젯, min/max 충돌)
  - Visibility issues (숨겨진 위젯)
  - Overlapping (좌표 기반 겹침 계산)
  - Layout issues (부모 없는 위젯)
  - Naming issues (의미 없는 이름)
- ✅ **Best Practices 검증**:
  - Theme Manager 사용 (`get_theme()`)
  - Themed Components 사용
  - 하드코딩 색상 검사 (#RRGGBB)
  - Object Names 사용
  - Docstrings 존재
- 📊 **HTML Report**: 저장 가능한 종합 리포트

### 장점
✅ 앱 실행 불필요
✅ HTML 리포트 저장
✅ Best practices 검증
✅ CI/CD 통합 가능
✅ 코드 품질 관리

### 단점
❌ 동적 생성 위젯 감지 불가
❌ 실제 렌더링 크기 모름
❌ 복잡한 표현식 제한적

---

## 3. Hot Reload - 개발 생산성

### 목적
파일 변경 시 앱 자동 재시작

### 사용 시기
- 개발 중 (항상!)
- UI 디자인 조정
- 테마 변경
- 코드 수정

### 사용 방법
```bash
python hot_reload.py
```

### 제공 기능
- 🔥 **Auto-restart**: `.py`, `.json` 파일 감지
- ⏱️ **1초 Debounce**: 중복 재시작 방지
- 📝 **Console Output**: 로그 유지
- 🛑 **Ctrl+C**: 종료

### 장점
✅ 수동 재시작 불필요
✅ 개발 속도 극대화
✅ 테마 변경 즉시 확인
✅ 생산성 향상

### 단점
❌ 분석 기능 없음
❌ 상태 유지 안됨 (재시작)

---

## 권장 워크플로우

### Phase 1: 개발 중
```bash
# Hot Reload 실행
python hot_reload.py

# 코드 수정 → 자동 재시작 → 확인 → 반복
```

### Phase 2: 디버깅
```python
# Visual Debugger 통합
from visual_debugger import launch_with_debugger

app = QApplication(sys.argv)
window = MainWindow()
debugger = launch_with_debugger(window)
sys.exit(app.exec())
```

**확인 사항:**
- Widget tree 구조
- 실제 렌더링 크기
- 스타일시트 적용 상태
- 위젯 가시성

### Phase 3: 코드 리뷰 전
```bash
# 정적 분석 실행
python gui_analyzer.py views/main_window.py
python gui_analyzer.py widgets/custom_card.py

# HTML 리포트 확인
# - Best practices 검증
# - 이슈 확인 및 수정
# - 리포트를 PR에 첨부
```

### Phase 4: CI/CD
```yaml
# GitHub Actions 예시
- name: Analyze GUI Code
  run: |
    python gui_analyzer.py views/*.py
    # 리포트를 artifact로 업로드
```

---

## 실전 예제

### 예제 1: 위젯이 보이지 않는 문제

**Step 1: Visual Debugger 실행**
```python
debugger = launch_with_debugger(window)
```

**Step 2: Widget Tree 확인**
- 위젯이 트리에 있는지 확인
- Visible = False인지 확인
- Geometry가 (0,0,0,0)인지 확인

**Step 3: Issues 탭 확인**
- "Widget is very small" 경고
- "Widget has no parent" 경고

**Step 4: 코드 수정**
```python
# Before
self.button = QPushButton("Click")  # 부모 없음

# After
self.button = QPushButton("Click", parent=self)
self.button.setMinimumSize(100, 40)
```

---

### 예제 2: 레이아웃 겹침 문제

**Step 1: GUI Analyzer 실행**
```bash
python gui_analyzer.py views/main_window.py
```

**Step 2: HTML 리포트 확인**
- Issues 섹션에서 "Widgets may overlap" 경고
- Widget Details 테이블에서 geometry 확인

**Step 3: 코드 수정**
```python
# Before - 수동 geometry 설정
self.button1.setGeometry(10, 10, 100, 50)
self.button2.setGeometry(15, 15, 100, 50)  # 겹침!

# After - Layout 사용
layout = QHBoxLayout()
layout.addWidget(self.button1)
layout.addWidget(self.button2)
```

---

### 예제 3: 테마 시스템 검증

**Step 1: GUI Analyzer 실행**
```bash
python gui_analyzer.py views/main_window.py
```

**Step 2: Best Practices 확인**
```
✅ Uses Theme Manager (get_theme())
✅ Uses Themed Components
❌ No Hardcoded Colors (found 5)
❌ Uses Object Names (setObjectName)
✅ Has Docstrings
```

**Step 3: 하드코딩 색상 수정**
```python
# Before
label.setStyleSheet("color: #ffffff; background: #1a1a1a;")

# After
theme = get_theme()
label = ThemedLabel("Text", style_type="primary")
```

**Step 4: Object Names 추가**
```python
self.submit_button.setObjectName("submit_button")
self.cancel_button.setObjectName("cancel_button")
```

**Step 5: 재검증**
```bash
python gui_analyzer.py views/main_window.py
# 모든 체크가 ✅로 변경됨
```

---

## 통합 개발 환경 구성

### 1. Demo Mode (Visual Debugger)
```python
# demo_mode.py
from visual_debugger import launch_with_debugger

app = QApplication(sys.argv)
window = MainWindow()
debugger = launch_with_debugger(window)
sys.exit(app.exec())
```

### 2. Hot Reload + Visual Debugger
```python
# hot_reload.py에서 demo_mode.py 실행
# 파일 변경 → 자동 재시작 → 디버거 자동 실행
```

### 3. Pre-commit Hook
```bash
# .git/hooks/pre-commit
#!/bin/bash
python gui_analyzer.py views/*.py
if [ $? -ne 0 ]; then
    echo "GUI analysis failed! Fix issues before committing."
    exit 1
fi
```

---

## 요약

### Visual Debugger
**언제:** 실행 중 디버깅
**무엇:** 실제 위젯 분석
**결과:** 실시간 인터랙션

### GUI Analyzer
**언제:** 코드 리뷰, PR 전
**무엇:** 정적 코드 분석
**결과:** HTML 리포트

### Hot Reload
**언제:** 개발 중 (항상)
**무엇:** 자동 재시작
**결과:** 생산성 향상

### 최고의 조합
```
Hot Reload (개발)
    → Visual Debugger (디버깅)
        → GUI Analyzer (검증)
            → 프로덕션 배포
```

---

## 참고 문서

- [skill.md](../skill.md) - PyQt/PySide Best Practices
- [README_GUI_ANALYZER.md](README_GUI_ANALYZER.md) - GUI Analyzer 상세 가이드
- [visual_debugger.py](../../../neurohub_client/visual_debugger.py) - Visual Debugger 소스
- [hot_reload.py](../../../neurohub_client/hot_reload.py) - Hot Reload 소스
- [GUI_ANALYSIS_REPORT.md](../../../neurohub_client/GUI_ANALYSIS_REPORT.md) - 분석 리포트 예시

---

**Copyright (c) 2025 F2X. All rights reserved.**
