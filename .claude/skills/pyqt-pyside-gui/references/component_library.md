# UI Components Library Guide

중앙화된 재사용 가능한 UI 컴포넌트 라이브러리입니다.

## 🎨 핵심 개념

### 1. 테마 중앙화
모든 색상, 폰트, 간격이 `AppTheme` 클래스에 정의되어 있습니다.
앱 전체에서 일관된 디자인을 유지할 수 있습니다.

### 2. 재사용 가능한 컴포넌트
자주 사용하는 UI 요소들을 미리 만들어두어 복사-붙여넣기 없이 사용합니다.

### 3. AI 친화적
명확한 구조와 네이밍으로 AI가 쉽게 이해하고 활용할 수 있습니다.

## 🚀 빠른 시작

### 기본 사용법

```python
from ui_components import (
    AppTheme,           # 테마 설정
    FormField,          # 폼 필드
    PrimaryButton,      # 버튼들
    Card,               # 카드 컨테이너
    HeaderSection       # 헤더
)

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # 배경색 설정
        central.setStyleSheet(f"background-color: {AppTheme.BACKGROUND};")
        
        # 헤더 추가
        header = HeaderSection("내 앱", "설명 텍스트")
        layout.addWidget(header.get_widget())
        
        # 카드 안에 폼 만들기
        card = Card("로그인")
        
        username = FormField("사용자명", required=True)
        card.add_widget(username.get_widget())
        
        password = FormField("비밀번호", field_type="password", required=True)
        card.add_widget(password.get_widget())
        
        # 버튼 그룹
        from ui_components import ButtonGroup
        buttons = ButtonGroup([
            {"text": "로그인", "type": "primary"},
            {"text": "취소", "type": "outline"}
        ])
        buttons.connect("로그인", self.login)
        card.add_widget(buttons.get_widget())
        
        layout.addWidget(card)
    
    def login(self):
        print("로그인 클릭!")
```

## 📦 사용 가능한 컴포넌트

### 테마 (AppTheme)

```python
# 색상 사용
AppTheme.PRIMARY          # #2563eb (파랑)
AppTheme.SUCCESS          # #16a34a (초록)
AppTheme.DANGER           # #dc2626 (빨강)
AppTheme.WARNING          # #ea580c (주황)

# 텍스트 색상
AppTheme.TEXT_PRIMARY     # 진한 텍스트
AppTheme.TEXT_SECONDARY   # 보조 텍스트

# 배경
AppTheme.BACKGROUND       # 앱 배경
AppTheme.SURFACE          # 카드 배경

# 간격
AppTheme.SPACING_SM       # 8px
AppTheme.SPACING_MD       # 12px
AppTheme.SPACING_LG       # 16px
AppTheme.SPACING_XL       # 24px

# 폰트 크기
AppTheme.FONT_SIZE_SM     # 12px
AppTheme.FONT_SIZE_BASE   # 14px
AppTheme.FONT_SIZE_LG     # 16px
AppTheme.FONT_SIZE_XL     # 20px
```

### 버튼

```python
# Primary Button - 주요 액션
button = PrimaryButton("저장")
button = PrimaryButton("저장", size="large")  # small, medium, large

# Secondary Button - 보조 액션
button = SecondaryButton("취소")

# Success Button - 성공/확인
button = SuccessButton("확인")

# Danger Button - 삭제/위험
button = DangerButton("삭제")

# Outline Button - 외곽선 버튼
button = OutlineButton("자세히")

# 클릭 이벤트 연결
button.clicked.connect(self.on_click)
```

### 폼 필드 (FormField)

```python
# 기본 텍스트 입력
field = FormField("이름", placeholder="홍길동")

# 필수 필드
field = FormField("이메일", required=True)

# 비밀번호 필드
field = FormField("비밀번호", field_type="password")

# 텍스트 에리어
field = FormField("메시지", field_type="text")

# 숫자 입력
field = FormField("나이", field_type="number")

# 도움말 텍스트
field = FormField("이메일", help_text="예: user@example.com")

# 값 가져오기/설정하기
field.get_value()
field.set_value("새 값")

# 유효성 검사
if field.is_valid():
    print("유효함")
else:
    field.show_error("이 필드는 필수입니다")

# 위젯 가져오기
layout.addWidget(field.get_widget())
```

### 카드 (Card)

```python
# 제목 있는 카드
card = Card("사용자 정보")

# 위젯 추가
card.add_widget(QLabel("내용"))

# 레이아웃 추가
inner_layout = QHBoxLayout()
card.add_layout(inner_layout)

# 카드를 레이아웃에 추가
layout.addWidget(card)
```

### 헤더 섹션 (HeaderSection)

```python
# 제목만
header = HeaderSection("페이지 제목")

# 제목 + 부제목
header = HeaderSection("페이지 제목", "설명 텍스트")

layout.addWidget(header.get_widget())
```

### 버튼 그룹 (ButtonGroup)

```python
# 여러 버튼을 그룹으로
buttons = ButtonGroup([
    {"text": "저장", "type": "primary"},
    {"text": "삭제", "type": "danger", "size": "medium"},
    {"text": "취소", "type": "outline"}
])

# 버튼에 이벤트 연결
buttons.connect("저장", self.save)
buttons.connect("삭제", self.delete)
buttons.connect("취소", self.cancel)

# 개별 버튼 가져오기
save_btn = buttons.get_button("저장")
save_btn.setEnabled(False)

# 정렬 (기본: right)
buttons = ButtonGroup([...], alignment="left")  # left, right

layout.addWidget(buttons.get_widget())
```

### 알림 (Alert)

```python
# 정보
alert = Alert("정보 메시지", "info")

# 성공
alert = Alert("저장되었습니다!", "success")

# 경고
alert = Alert("주의가 필요합니다", "warning")

# 에러
alert = Alert("오류가 발생했습니다", "danger")

layout.addWidget(alert)
```

### 구분선 & 간격

```python
# 구분선
layout.addWidget(Divider())

# 간격
layout.addWidget(Spacer())              # 기본 (16px)
layout.addWidget(Spacer("small"))       # 8px
layout.addWidget(Spacer("large"))       # 24px
```

## 🎯 실전 예제

### 예제 1: 로그인 폼

```python
from ui_components import *

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("로그인")
        self.setGeometry(100, 100, 400, 500)
        
        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"background-color: {AppTheme.BACKGROUND};")
        self.setCentralWidget(scroll)
        
        # 컨테이너
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(
            AppTheme.SPACING_XL, AppTheme.SPACING_XL,
            AppTheme.SPACING_XL, AppTheme.SPACING_XL
        )
        
        # 헤더
        header = HeaderSection("로그인", "계정에 로그인하세요")
        layout.addWidget(header.get_widget())
        
        # 폼 카드
        card = Card()
        
        self.username = FormField("사용자명", required=True, 
                                  placeholder="이메일 또는 사용자명")
        card.add_widget(self.username.get_widget())
        
        self.password = FormField("비밀번호", field_type="password", 
                                  required=True)
        card.add_widget(self.password.get_widget())
        
        # 버튼
        buttons = ButtonGroup([
            {"text": "로그인", "type": "primary"},
            {"text": "취소", "type": "outline"}
        ])
        buttons.connect("로그인", self.login)
        buttons.connect("취소", self.close)
        card.add_widget(buttons.get_widget())
        
        layout.addWidget(card)
        layout.addStretch()
        
        scroll.setWidget(container)
    
    def login(self):
        # 유효성 검사
        if not self.username.is_valid():
            self.username.show_error("사용자명을 입력하세요")
            return
        
        if not self.password.is_valid():
            self.password.show_error("비밀번호를 입력하세요")
            return
        
        # 로그인 처리
        username = self.username.get_value()
        password = self.password.get_value()
        
        print(f"로그인: {username}")
```

### 예제 2: 사용자 프로필 폼

```python
class ProfileWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("프로필")
        self.setGeometry(100, 100, 600, 700)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"background-color: {AppTheme.BACKGROUND};")
        self.setCentralWidget(scroll)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(
            AppTheme.SPACING_XL, AppTheme.SPACING_XL,
            AppTheme.SPACING_XL, AppTheme.SPACING_XL
        )
        layout.setSpacing(AppTheme.SPACING_LG)
        
        # 헤더
        header = HeaderSection("내 프로필", "개인 정보를 관리하세요")
        layout.addWidget(header.get_widget())
        
        # 기본 정보 카드
        basic_card = Card("기본 정보")
        
        self.name = FormField("이름", required=True)
        basic_card.add_widget(self.name.get_widget())
        
        self.email = FormField("이메일", required=True,
                               help_text="이메일 주소는 공개되지 않습니다")
        basic_card.add_widget(self.email.get_widget())
        
        self.phone = FormField("전화번호", placeholder="010-0000-0000")
        basic_card.add_widget(self.phone.get_widget())
        
        layout.addWidget(basic_card)
        
        # 추가 정보 카드
        extra_card = Card("추가 정보")
        
        self.bio = FormField("자기소개", field_type="text",
                            placeholder="간단히 자신을 소개해주세요...")
        extra_card.add_widget(self.bio.get_widget())
        
        layout.addWidget(extra_card)
        
        # 알림
        layout.addWidget(Alert("변경사항은 자동으로 저장됩니다", "info"))
        
        # 버튼
        buttons = ButtonGroup([
            {"text": "저장", "type": "success"},
            {"text": "취소", "type": "outline"}
        ])
        buttons.connect("저장", self.save)
        buttons.connect("취소", self.close)
        layout.addWidget(buttons.get_widget())
        
        layout.addStretch()
        scroll.setWidget(container)
    
    def save(self):
        # 유효성 검사
        if not self.name.is_valid():
            self.name.show_error("이름을 입력하세요")
            return
        
        if not self.email.is_valid():
            self.email.show_error("이메일을 입력하세요")
            return
        
        # 저장 처리
        data = {
            "name": self.name.get_value(),
            "email": self.email.get_value(),
            "phone": self.phone.get_value(),
            "bio": self.bio.get_value()
        }
        
        print(f"저장: {data}")
        
        # 성공 메시지
        QMessageBox.information(self, "성공", "프로필이 저장되었습니다")
```

## 🎨 테마 커스터마이징

테마를 원하는 대로 변경할 수 있습니다:

```python
# ui_components.py의 AppTheme 클래스 수정

class AppTheme:
    # 색상 팔레트를 원하는 색으로 변경
    PRIMARY = "#your_color"
    SUCCESS = "#your_color"
    # ...
```

## 💡 AI와 함께 사용하기

### AI에게 요청하는 방법

```
✅ 좋은 예:
"ui_components를 사용해서 로그인 폼을 만들어줘.
FormField로 사용자명과 비밀번호 필드를 만들고,
ButtonGroup으로 로그인과 취소 버튼을 추가해줘.
전체를 Card 안에 넣어줘."

✅ 좋은 예:
"Card 안에 3개의 FormField를 추가해줘:
1. 이름 (required)
2. 이메일 (required, help_text 추가)
3. 메시지 (field_type="text")
그리고 PrimaryButton으로 제출 버튼 추가"

❌ 나쁜 예:
"폼 만들어줘"  (어떤 컴포넌트를 사용할지 불명확)
```

### 컴포넌트 목록 전달

AI에게 작업을 요청할 때 사용 가능한 컴포넌트를 알려주세요:

```
"ui_components 라이브러리가 있어. 사용 가능한 컴포넌트:
- FormField: 폼 필드 (field_type: line, text, password, number)
- PrimaryButton, SecondaryButton, SuccessButton, DangerButton
- Card: 카드 컨테이너
- HeaderSection: 헤더
- ButtonGroup: 버튼 그룹
- Alert: 알림 (type: info, success, warning, danger)
- AppTheme: 테마 상수

이것들을 사용해서 회원가입 폼을 만들어줘"
```

## 📋 체크리스트

컴포넌트 사용 시:

- [ ] `from ui_components import *` 임포트
- [ ] 배경색은 `AppTheme.BACKGROUND` 사용
- [ ] 간격은 `AppTheme.SPACING_*` 사용
- [ ] 모든 위젯에 objectName 설정
- [ ] 핫 리로드로 실시간 확인

## 🎉 장점

1. **일관성**: 앱 전체가 동일한 디자인 유지
2. **생산성**: 컴포넌트 재사용으로 빠른 개발
3. **유지보수**: 테마 한 곳만 수정하면 전체 적용
4. **AI 친화적**: 명확한 구조로 AI가 쉽게 사용
5. **확장성**: 새 컴포넌트 추가 용이

이제 일관되고 아름다운 GUI를 빠르게 만들 수 있습니다! 🚀
