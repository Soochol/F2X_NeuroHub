# Qt Stylesheet (QSS) Reference Guide

Complete guide for styling Qt applications with stylesheets.

## Basic Syntax

```css
Selector {
    property: value;
}
```

## Common Selectors

### Widget Type Selectors
```css
QPushButton { }          /* All QPushButton widgets */
QLabel { }               /* All QLabel widgets */
QLineEdit { }            /* All QLineEdit widgets */
```

### Class Selectors
```css
.QPushButton { }         /* Only QPushButton, not subclasses */
```

### ID Selectors
```css
#myButton { }            /* Widget with objectName "myButton" */
```

### State Selectors
```css
QPushButton:hover { }    /* When mouse hovers */
QPushButton:pressed { }  /* When pressed */
QPushButton:disabled { } /* When disabled */
QPushButton:checked { }  /* When checked (checkable buttons) */
QPushButton:focus { }    /* When has focus */
```

### Descendant Selectors
```css
QDialog QPushButton { }  /* QPushButton inside QDialog */
```

## Common Properties

### Colors and Backgrounds

```css
QWidget {
    color: #333333;                    /* Text color */
    background-color: #FFFFFF;         /* Background color */
    border: 1px solid #CCCCCC;        /* Border */
    background: qlineargradient(       /* Gradient background */
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFFFFF,
        stop:1 #E0E0E0
    );
}
```

### Typography

```css
QLabel {
    font-family: "Arial", sans-serif;
    font-size: 14px;
    font-weight: bold;                 /* normal, bold, 100-900 */
    font-style: italic;                /* normal, italic, oblique */
    text-decoration: underline;        /* none, underline, overline, line-through */
}
```

### Spacing and Sizing

```css
QPushButton {
    padding: 8px 16px;                 /* top/bottom left/right */
    margin: 4px;
    min-width: 80px;
    max-width: 200px;
    min-height: 30px;
    max-height: 50px;
}
```

### Borders and Corners

```css
QLineEdit {
    border: 2px solid #2196F3;
    border-radius: 5px;                /* Rounded corners */
    border-top-left-radius: 10px;      /* Individual corners */
    border-style: solid;               /* solid, dashed, dotted, etc. */
}
```

## Widget-Specific Examples

### QPushButton

```css
QPushButton {
    background-color: #2196F3;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1976D2;
}

QPushButton:pressed {
    background-color: #0D47A1;
}

QPushButton:disabled {
    background-color: #BDBDBD;
    color: #757575;
}
```

### QLineEdit

```css
QLineEdit {
    border: 2px solid #E0E0E0;
    border-radius: 4px;
    padding: 6px;
    background-color: white;
    selection-background-color: #2196F3;
    selection-color: white;
}

QLineEdit:focus {
    border: 2px solid #2196F3;
}

QLineEdit:disabled {
    background-color: #F5F5F5;
    color: #9E9E9E;
}
```

### QComboBox

```css
QComboBox {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 5px;
    background-color: white;
}

QComboBox:hover {
    border: 1px solid #2196F3;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: url(down_arrow.png);
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    border: 1px solid #CCCCCC;
    background-color: white;
    selection-background-color: #2196F3;
    selection-color: white;
}
```

### QTableView

```css
QTableView {
    gridline-color: #E0E0E0;
    background-color: white;
    alternate-background-color: #F5F5F5;
    selection-background-color: #2196F3;
    selection-color: white;
}

QTableView::item {
    padding: 5px;
}

QTableView::item:hover {
    background-color: #E3F2FD;
}

QHeaderView::section {
    background-color: #F5F5F5;
    padding: 6px;
    border: 1px solid #E0E0E0;
    font-weight: bold;
}
```

### QTabWidget

```css
QTabWidget::pane {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    top: -1px;
}

QTabBar::tab {
    background-color: #F5F5F5;
    border: 1px solid #CCCCCC;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: white;
    border-bottom: none;
}

QTabBar::tab:hover {
    background-color: #E3F2FD;
}
```

### QScrollBar

```css
QScrollBar:vertical {
    border: none;
    background-color: #F5F5F5;
    width: 12px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #BDBDBD;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #9E9E9E;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}
```

### QProgressBar

```css
QProgressBar {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    text-align: center;
    background-color: #F5F5F5;
}

QProgressBar::chunk {
    background-color: #4CAF50;
    border-radius: 3px;
}
```

## Complete Theme Examples

### Modern Dark Theme

```css
* {
    background-color: #2B2B2B;
    color: #FFFFFF;
    border: none;
}

QPushButton {
    background-color: #3C3C3C;
    border: 1px solid #505050;
    border-radius: 4px;
    padding: 6px 12px;
}

QPushButton:hover {
    background-color: #505050;
}

QPushButton:pressed {
    background-color: #2B2B2B;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #3C3C3C;
    border: 1px solid #505050;
    border-radius: 4px;
    padding: 4px;
    selection-background-color: #0D47A1;
}

QLabel {
    background-color: transparent;
}
```

### Material Design Light Theme

```css
* {
    font-family: "Roboto", "Arial", sans-serif;
}

QPushButton {
    background-color: #2196F3;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: 500;
    text-transform: uppercase;
}

QPushButton:hover {
    background-color: #1976D2;
}

QPushButton:pressed {
    background-color: #0D47A1;
}

QLineEdit {
    border: none;
    border-bottom: 2px solid #BDBDBD;
    background-color: transparent;
    padding: 6px 0;
}

QLineEdit:focus {
    border-bottom: 2px solid #2196F3;
}
```

## Tips and Best Practices

1. **Use object names for specific styling**
```python
button.setObjectName("primaryButton")
# In stylesheet: #primaryButton { }
```

2. **Load stylesheets from file**
```python
from pathlib import Path
stylesheet = Path("style.qss").read_text()
app.setStyleSheet(stylesheet)
```

3. **Combine multiple selectors**
```css
QPushButton, QToolButton {
    /* Applies to both */
}
```

4. **Use variables (not natively supported, but can preprocess)**
```python
PRIMARY_COLOR = "#2196F3"
stylesheet = f"""
    QPushButton {{
        background-color: {PRIMARY_COLOR};
    }}
"""
```

5. **Performance considerations**
- Apply stylesheets to parent widgets when possible
- Avoid overly complex selectors
- Cache compiled stylesheets

## Common Issues

### Issue: Styles not applying
**Solution**: Check selector specificity, ensure objectName is set, verify syntax

### Issue: Backgrounds not showing
**Solution**: Set `autoFillBackground` to `True` or use proper background property

### Issue: Layout issues after styling
**Solution**: Adjust padding/margins, check size policies
