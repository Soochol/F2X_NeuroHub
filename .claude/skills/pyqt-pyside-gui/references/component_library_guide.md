# Component Library & Theme System Guide

Complete guide to using the centralized component library with consistent theming.

## Quick Start

### 1. Import Components

```python
import sys
sys.path.insert(0, '/path/to/pyqt-pyside-gui/scripts')

from ui_components import *
```

### 2. Load and Apply Theme

```python
app = QApplication(sys.argv)
load_theme(app, "default")  # Load and apply theme to entire app
# or use "dark" for dark theme: load_theme(app, "dark")
```

### 3. Use Components

```python
# Create button
button = Button("Click Me", variant="primary")
layout.addWidget(button.get_widget())

# Create form field
email = FormField("Email", required=True)
layout.addWidget(email.get_widget())
```

## Available Components

### Button
Themed button with multiple variants.

```python
# Primary button
btn = Button("Save", variant="primary", size="normal")
btn.clicked.connect(on_save)

# Other variants
btn_secondary = Button("Cancel", variant="secondary")
btn_success = Button("Submit", variant="success")
btn_danger = Button("Delete", variant="danger")
btn_warning = Button("Warning", variant="warning")
btn_outline = Button("Outline", variant="outline")
btn_text = Button("Text Only", variant="text")

# Sizes
btn_small = Button("Small", size="small")
btn_large = Button("Large", size="large")

# With minimum width
btn_wide = Button("Wide Button", min_width=200)
```

### Input
Text input with validation support.

```python
# Simple input
name_input = Input(placeholder="Enter name...")
name_input.textChanged.connect(on_text_change)

# Password input
password = Input(placeholder="Password", password=True)

# Multiline input
bio = Input(placeholder="Bio...", multiline=True)

# Read-only
display = Input(read_only=True)
display.set_value("Read-only text")

# Get/set value
value = name_input.get_value()
name_input.set_value("New value")
```

### Label
Styled text label.

```python
# Title
title = Label("Page Title", variant="title", alignment=Qt.AlignCenter)

# Heading
heading = Label("Section", variant="heading")

# Normal text
text = Label("Description text", variant="normal")

# Small/caption
small = Label("Caption", variant="small")

# Update text
title.set_text("New Title")
```

### FormField
Complete form field with label, input, validation, and error display.

```python
# Basic field
email = FormField("Email", placeholder="user@example.com", required=True)

# With validator
def validate_email(value):
    if "@" not in value:
        return False, "Invalid email format"
    return True, ""

email = FormField(
    "Email",
    placeholder="user@example.com",
    required=True,
    validator=validate_email,
    help_text="We'll never share your email"
)

# Different input types
name = FormField("Name", input_type="text")
password = FormField("Password", input_type="password")
bio = FormField("Bio", input_type="multiline")
age = FormField("Age", input_type="number")
price = FormField("Price", input_type="decimal")

# Get/set value
value = email.get_value()
email.set_value("new@email.com")

# Validate
if email.validate():
    print("Valid!")

# Show custom error
email.show_error("Custom error message")
email.clear_error()
```

### Card
Container with optional title and styling.

```python
# Simple card
card = Card()
card.add_widget(some_widget)

# Card with title
user_card = Card(title="User Information")

# Add components
user_card.add_component(name_field)
user_card.add_component(email_field)

# Add regular widgets
user_card.add_widget(some_qt_widget)

# Custom padding
card = Card(title="Title", padding=Spacing.LARGE)
```

### ButtonGroup
Group of buttons with consistent spacing.

```python
# Right-aligned (default)
buttons = ButtonGroup([
    {
        "text": "Save",
        "variant": "success",
        "callback": on_save,
        "min_width": 100
    },
    {
        "text": "Cancel",
        "variant": "secondary",
        "callback": on_cancel
    }
])

layout.addWidget(buttons.get_widget())

# Get individual button
save_btn = buttons.get_button("Save")
save_btn.set_enabled(False)

# Different alignments
left_buttons = ButtonGroup(buttons_config, alignment="left")
center_buttons = ButtonGroup(buttons_config, alignment="center")
```

## Layout Helpers

### create_form_layout
Create vertical form layout.

```python
form = create_form_layout(
    name_field,
    email_field,
    password_field
)

container.layout().addWidget(form)
```

### create_horizontal_group
Create horizontal layout with items.

```python
# With stretch
row = create_horizontal_group(
    label,
    "stretch",  # Adds stretch
    button
)

# Custom spacing
row = create_horizontal_group(
    item1, item2, item3,
    spacing=Spacing.LARGE
)
```

## Theming System

### Color Palette
All colors defined in one place.

```python
# Primary colors
ColorPalette.PRIMARY          # #3498db
ColorPalette.PRIMARY_DARK     # #2980b9
ColorPalette.PRIMARY_LIGHT    # #5dade2

# Semantic colors
ColorPalette.SUCCESS          # #2ecc71
ColorPalette.DANGER           # #e74c3c
ColorPalette.WARNING          # #f39c12
ColorPalette.INFO             # #3498db

# Text colors
ColorPalette.TEXT_PRIMARY     # #2c3e50
ColorPalette.TEXT_SECONDARY   # #7f8c8d
ColorPalette.TEXT_DISABLED    # #bdc3c7

# Backgrounds
ColorPalette.BACKGROUND        # #ecf0f1
ColorPalette.BACKGROUND_PAPER  # #ffffff
```

### Typography

```python
# Font sizes
Typography.FONT_SIZE_XLARGE   # 24
Typography.FONT_SIZE_LARGE    # 18
Typography.FONT_SIZE_NORMAL   # 14
Typography.FONT_SIZE_SMALL    # 12

# Font weights
Typography.FONT_WEIGHT_BOLD   # 700
Typography.FONT_WEIGHT_MEDIUM # 500
Typography.FONT_WEIGHT_NORMAL # 400
```

### Spacing

```python
Spacing.XXSMALL   # 2px
Spacing.XSMALL    # 4px
Spacing.SMALL     # 8px
Spacing.NORMAL    # 12px
Spacing.MEDIUM    # 16px
Spacing.LARGE     # 24px
Spacing.XLARGE    # 32px
Spacing.XXLARGE   # 48px
```

### Border Radius

```python
BorderRadius.NONE     # 0
BorderRadius.SMALL    # 2px
BorderRadius.NORMAL   # 4px
BorderRadius.MEDIUM   # 6px
BorderRadius.LARGE    # 8px
BorderRadius.ROUND    # 9999px (fully rounded)
```

## Customizing the Theme

**Note:** This component library uses a JSON-based theme system. For complete theming documentation, see [json_theme_guide.md](json_theme_guide.md).

### Method 1: Modify JSON theme files

```python
# Modify ui_components/themes/default.json
{
  "colors": {
    "primary": {
      "main": "#FF5722"  // Change to your brand color
    }
  }
}

# Load the modified theme
load_theme(app, "default")
```

### Method 2: Create custom theme

```bash
# Copy existing theme
cp ui_components/themes/default.json ui_components/themes/my-theme.json

# Modify colors, typography, spacing in JSON file
# Then load your custom theme
```

```python
load_theme(app, "my-theme")
```

### Method 3: Runtime theme switching

```python
# Switch between themes at runtime
load_theme(app, "dark")   # Switch to dark theme
load_theme(app, "default")  # Switch back to default
```

### Method 4: Per-widget customization

```python
# Create component with custom style
button = Button("Custom", variant="primary")
button.get_widget().setStyleSheet("""
    QPushButton {
        background-color: #FF5722;
        font-size: 16px;
    }
""")
```

## Complete Example

```python
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt

sys.path.insert(0, '/path/to/scripts')
from ui_components import *


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Application")
        self.setGeometry(100, 100, 600, 500)
        self.setup_ui()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setSpacing(Spacing.LARGE)
        layout.setContentsMargins(
            Spacing.LARGE, Spacing.LARGE,
            Spacing.LARGE, Spacing.LARGE
        )
        
        # Title
        title = Label("Welcome", variant="title", alignment=Qt.AlignCenter)
        layout.addWidget(title.get_widget())
        
        # Form card
        form_card = Card(title="Login")
        
        self.email = FormField("Email", required=True)
        form_card.add_component(self.email)
        
        self.password = FormField("Password", input_type="password", required=True)
        form_card.add_component(self.password)
        
        layout.addWidget(form_card.get_widget())
        layout.addStretch()
        
        # Buttons
        buttons = ButtonGroup([
            {"text": "Login", "variant": "primary", "callback": self.login},
            {"text": "Cancel", "variant": "secondary", "callback": self.close}
        ])
        layout.addWidget(buttons.get_widget())

    def login(self):
        if self.email.validate() and self.password.validate():
            print(f"Login: {self.email.get_value()}")


def main():
    app = QApplication(sys.argv)
    load_theme(app, "default")
    
    window = MyApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

## Best Practices

### 1. Always Use Components
❌ Bad:
```python
button = QPushButton("Save")
button.setStyleSheet("QPushButton { background: blue; }")
```

✅ Good:
```python
button = Button("Save", variant="primary")
```

### 2. Use Theme Constants
❌ Bad:
```python
layout.setSpacing(10)
label.setStyleSheet("color: #333333;")
```

✅ Good:
```python
layout.setSpacing(Spacing.NORMAL)
label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY};")
```

### 3. Set Object Names
✅ Always:
```python
# Components automatically set object names, but for custom widgets:
widget.setObjectName("my_custom_widget")
```

### 4. Validate Forms Properly
```python
# Validate all fields before submission
fields = [name_field, email_field, password_field]
if all(field.validate() for field in fields):
    # Process form
    pass
```

### 5. Use Cards for Grouping
```python
# Group related fields in cards
user_info_card = Card(title="User Information")
user_info_card.add_component(name_field)
user_info_card.add_component(email_field)

account_card = Card(title="Account")
account_card.add_component(username_field)
account_card.add_component(password_field)
```

## Requesting AI Changes

### ❌ Bad Request
"Make the button blue"

### ✅ Good Request
"Change the button variant from 'secondary' to 'primary'"

### ❌ Bad Request
"Add more space between elements"

### ✅ Good Request
"Change the layout spacing from Spacing.NORMAL to Spacing.LARGE"

### ❌ Bad Request
"The form looks bad"

### ✅ Good Request
"Add a Card component around the form fields with title 'User Information'. Use Spacing.LARGE for padding."

## Troubleshooting

### Components Not Found
```python
# Make sure path is correct
import sys
sys.path.insert(0, '/home/claude/pyqt-pyside-gui/scripts')
from ui_components import *
```

### Theme Not Applied
```python
# Must call load_theme BEFORE creating windows
app = QApplication(sys.argv)
load_theme(app, "default")  # <-- Do this first
window = MainWindow()        # <-- Then create window
```

### Validation Not Working
```python
# Must call validate() or check is_valid
if form_field.validate():  # <-- Returns True/False
    # Field is valid
```

### Custom Styles Overridden
```python
# Apply custom styles AFTER getting widget
button = Button("Text")
widget = button.get_widget()  # <-- Get widget first
widget.setStyleSheet("...")   # <-- Then customize
```
