# AI-Friendly Development Patterns

Patterns and practices that make GUI development with AI assistance more effective.

## Why Special Patterns for AI?

AI assistants excel at generating code but struggle with:
- Visual feedback (can't see the UI)
- Understanding spatial relationships
- Debugging layout issues
- Iterating on visual design

These patterns solve these problems by making the code more explicit, testable, and debuggable.

## Pattern 1: Component-Based Architecture

Break UI into self-contained, reusable components.

### Benefits for AI Development
- Smaller, focused pieces AI can handle better
- Easy to test individual components
- Clear boundaries and contracts
- Can be debugged in isolation

### Base Component Template

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal

class UIComponent:
    """Base class for reusable UI components"""
    
    def __init__(self):
        self.widget = None
        self._signals = {}
        
    def create(self):
        """Create and return the widget - override in subclasses"""
        raise NotImplementedError
        
    def get_widget(self):
        """Get the widget instance"""
        if self.widget is None:
            self.widget = self.create()
        return self.widget
    
    def get_value(self):
        """Get component value - override if component has data"""
        return None
    
    def set_value(self, value):
        """Set component value - override if component has data"""
        pass
```

### Example: Form Field Component

```python
class FormFieldComponent(UIComponent):
    """Reusable form field with label and input"""
    
    def __init__(self, label_text, field_type="line_edit", 
                 placeholder="", required=False):
        super().__init__()
        self.label_text = label_text
        self.field_type = field_type
        self.placeholder = placeholder
        self.required = required
        self.field = None
    
    def create(self):
        from PySide6.QtWidgets import (
            QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit
        )
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 10)
        layout.setSpacing(5)
        
        # Label with required indicator
        label_text = self.label_text
        if self.required:
            label_text += " *"
        
        label = QLabel(label_text)
        label.setObjectName(f"label_{self.label_text.lower().replace(' ', '_')}")
        label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 500;
                color: #2c3e50;
            }
        """)
        layout.addWidget(label)
        
        # Input field
        if self.field_type == "line_edit":
            self.field = QLineEdit()
            self.field.setPlaceholderText(self.placeholder)
        elif self.field_type == "text_edit":
            self.field = QTextEdit()
            self.field.setPlaceholderText(self.placeholder)
            self.field.setMaximumHeight(100)
        
        self.field.setObjectName(f"input_{self.label_text.lower().replace(' ', '_')}")
        self.field.setStyleSheet("""
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        
        layout.addWidget(self.field)
        
        return container
    
    def get_value(self):
        """Get field value"""
        from PySide6.QtWidgets import QLineEdit, QTextEdit
        
        if isinstance(self.field, QLineEdit):
            return self.field.text()
        elif isinstance(self.field, QTextEdit):
            return self.field.toPlainText()
        return None
    
    def set_value(self, value):
        """Set field value"""
        from PySide6.QtWidgets import QLineEdit, QTextEdit
        
        if isinstance(self.field, QLineEdit):
            self.field.setText(str(value))
        elif isinstance(self.field, QTextEdit):
            self.field.setPlainText(str(value))
    
    def is_valid(self):
        """Check if field is valid"""
        if self.required:
            value = self.get_value()
            return value is not None and len(value.strip()) > 0
        return True
```

### Using Components

```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create components
        self.name_field = FormFieldComponent("Name", required=True)
        self.email_field = FormFieldComponent("Email", placeholder="user@example.com")
        self.message_field = FormFieldComponent("Message", field_type="text_edit")
        
        # Add to layout
        layout.addWidget(self.name_field.get_widget())
        layout.addWidget(self.email_field.get_widget())
        layout.addWidget(self.message_field.get_widget())
        
    def submit_form(self):
        """Validate and submit"""
        if not self.name_field.is_valid():
            QMessageBox.warning(self, "Error", "Name is required")
            return
        
        data = {
            "name": self.name_field.get_value(),
            "email": self.email_field.get_value(),
            "message": self.message_field.get_value()
        }
        print(f"Submitted: {data}")
```

## Pattern 2: Declarative UI Definition

Define UI structure in a clear, declarative way that AI can easily generate and modify.

```python
class DeclarativeWindow(QMainWindow):
    """Window with declarative UI structure"""
    
    def __init__(self):
        super().__init__()
        self.components = {}
        self.build_ui(self.get_ui_structure())
    
    def get_ui_structure(self):
        """Define UI structure declaratively"""
        return {
            "type": "window",
            "title": "My Application",
            "size": (800, 600),
            "layout": {
                "type": "vertical",
                "spacing": 10,
                "margins": (20, 20, 20, 20),
                "children": [
                    {
                        "type": "label",
                        "name": "title",
                        "text": "Welcome",
                        "style": "font-size: 24px; font-weight: bold;"
                    },
                    {
                        "type": "horizontal_line"
                    },
                    {
                        "type": "form_field",
                        "name": "username",
                        "label": "Username",
                        "required": True
                    },
                    {
                        "type": "form_field",
                        "name": "password",
                        "label": "Password",
                        "field_type": "password",
                        "required": True
                    },
                    {
                        "type": "button_group",
                        "buttons": [
                            {"name": "login", "text": "Login", "color": "primary"},
                            {"name": "cancel", "text": "Cancel", "color": "secondary"}
                        ]
                    }
                ]
            }
        }
    
    def build_ui(self, structure):
        """Build UI from structure"""
        # Implementation...
        pass
```

## Pattern 3: Explicit Size and Spacing

Make all sizes, spacing, and margins explicit to avoid layout issues.

### Good: Explicit Dimensions

```python
# ✓ Good - explicit and predictable
button = QPushButton("Click Me")
button.setMinimumWidth(120)
button.setMaximumHeight(40)
button.setFixedHeight(40)

layout = QVBoxLayout()
layout.setContentsMargins(20, 20, 20, 20)  # explicit margins
layout.setSpacing(10)  # explicit spacing
```

### Bad: Implicit Sizing

```python
# ✗ Bad - relies on default behavior
button = QPushButton("Click Me")  # size unknown

layout = QVBoxLayout()  # default margins/spacing
```

## Pattern 4: Named Object References

Always set objectName for widgets you'll reference or debug.

```python
# ✓ Good - named for debugging
self.submit_button = QPushButton("Submit")
self.submit_button.setObjectName("submit_button")

self.email_input = QLineEdit()
self.email_input.setObjectName("email_input")

# Now easy to find in debugger:
# - Visual debugger shows "submit_button" instead of "QPushButton"
# - CSS can target #submit_button
# - AI can reference by name
```

## Pattern 5: Style Constants

Define colors, fonts, and sizes as constants.

```python
class AppStyle:
    """Centralized style constants"""
    
    # Colors
    PRIMARY_COLOR = "#3498db"
    SECONDARY_COLOR = "#95a5a6"
    SUCCESS_COLOR = "#2ecc71"
    DANGER_COLOR = "#e74c3c"
    WARNING_COLOR = "#f39c12"
    
    TEXT_PRIMARY = "#2c3e50"
    TEXT_SECONDARY = "#7f8c8d"
    
    BACKGROUND = "#ecf0f1"
    SURFACE = "#ffffff"
    
    # Sizes
    FONT_SIZE_LARGE = 18
    FONT_SIZE_NORMAL = 14
    FONT_SIZE_SMALL = 12
    
    SPACING_LARGE = 20
    SPACING_NORMAL = 10
    SPACING_SMALL = 5
    
    BORDER_RADIUS = 4
    
    @staticmethod
    def button_style(color="primary"):
        """Get button stylesheet"""
        colors = {
            "primary": AppStyle.PRIMARY_COLOR,
            "secondary": AppStyle.SECONDARY_COLOR,
            "success": AppStyle.SUCCESS_COLOR,
            "danger": AppStyle.DANGER_COLOR,
        }
        
        bg_color = colors.get(color, AppStyle.PRIMARY_COLOR)
        
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                border-radius: {AppStyle.BORDER_RADIUS}px;
                padding: {AppStyle.SPACING_NORMAL}px {AppStyle.SPACING_LARGE}px;
                font-size: {AppStyle.FONT_SIZE_NORMAL}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {bg_color}dd;
            }}
            QPushButton:pressed {{
                background-color: {bg_color}bb;
            }}
        """

# Usage
button = QPushButton("Save")
button.setStyleSheet(AppStyle.button_style("success"))
```

## Pattern 6: Validation and Feedback

Build validation into components with clear visual feedback.

```python
class ValidatedLineEdit(QLineEdit):
    """Line edit with built-in validation feedback"""
    
    def __init__(self, validator_fn=None, error_message="Invalid input"):
        super().__init__()
        self.validator_fn = validator_fn
        self.error_message = error_message
        self._is_valid = True
        
        self.textChanged.connect(self._on_text_changed)
    
    def _on_text_changed(self):
        """Validate on text change"""
        if self.validator_fn:
            self._is_valid = self.validator_fn(self.text())
            self._update_style()
    
    def _update_style(self):
        """Update visual style based on validation"""
        if self._is_valid:
            self.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #2ecc71;
                    background-color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #e74c3c;
                    background-color: #ffe6e6;
                }
            """)
    
    def is_valid(self):
        """Check if current value is valid"""
        return self._is_valid

# Usage
email_input = ValidatedLineEdit(
    validator_fn=lambda text: "@" in text and "." in text,
    error_message="Please enter a valid email"
)
```

## Pattern 7: AI Instruction Comments

Add structured comments that help AI understand your intent.

```python
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """
        UI Structure:
        - Header (60px height, blue background)
          - Title label (left-aligned)
          - User menu button (right-aligned)
        - Main content area (flexible height)
          - Sidebar (200px width, gray background)
            - Navigation buttons
          - Content panel (flexible width)
            - Dynamic content based on navigation
        - Footer (40px height, dark gray)
          - Status text (left)
          - Version label (right)
        """
        
        # Header section - REQUIREMENT: fixed 60px height, blue bg
        header = self._create_header()
        
        # Main section - REQUIREMENT: takes remaining space
        main = self._create_main_content()
        
        # Footer section - REQUIREMENT: fixed 40px height
        footer = self._create_footer()
        
        # Assemble - REQUIREMENT: vertical layout, no spacing
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(header)
        layout.addWidget(main, stretch=1)  # stretch=1 means take remaining space
        layout.addWidget(footer)
        
        self.setCentralWidget(central)
```

## Communicating Issues to AI

When something doesn't look right, describe it precisely:

### Bad Communication
❌ "The layout is wrong"
❌ "It doesn't look good"
❌ "Fix the UI"

### Good Communication
✅ "The submit button is hidden. Looking at the visual debugger, it shows the button has size 0×0. The button should be 120px wide and 40px tall."

✅ "The text color is hard to read. The label currently uses #333333 on a #666666 background. Change it to use AppStyle.TEXT_PRIMARY (#2c3e50) on AppStyle.SURFACE (#ffffff)."

✅ "The form fields are overlapping. The visual debugger shows no spacing between them. Add 10px spacing to the vertical layout."

## Debugging Checklist

When UI doesn't look right, check in this order:

1. **Is widget visible?** (Check visual debugger tree)
2. **Is widget size > 0?** (Check inspector panel)
3. **Does parent have layout?** (Check layout info)
4. **Are margins/spacing reasonable?** (Check layout margins)
5. **Are size policies correct?** (Check size policy in inspector)
6. **Is stylesheet correct?** (Check style panel)

## Summary: AI-Friendly Workflow

1. **Define structure** in components or declarative format
2. **Make sizes explicit** - no implicit sizing
3. **Use constants** for colors, fonts, spacing
4. **Name everything** with objectName
5. **Add comments** describing visual requirements
6. **Test incrementally** with hot reload
7. **Debug visually** when issues arise
8. **Communicate precisely** about problems
