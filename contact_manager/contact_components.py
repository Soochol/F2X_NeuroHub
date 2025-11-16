"""
Contact Manager Reusable Components

Custom components extending ui_components.BaseComponent for the contact manager app.
These components can be reused in other projects that need contact management UI.
"""

import sys
from pathlib import Path
from typing import Optional, Callable

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Signal

# Add ui_components to path
UI_COMPONENTS_PATH = Path(__file__).parent.parent / ".claude" / "skills" / "pyqt-pyside-gui" / "scripts"
sys.path.insert(0, str(UI_COMPONENTS_PATH))

from ui_components.components import BaseComponent, get_current_theme
from ui_components import Button, Input, Label, FormField, Card, ButtonGroup, Spacing


class ContactCard(BaseComponent):
    """
    Reusable contact card component

    Displays contact information with edit and delete actions.

    Usage:
        from models import Contact
        contact = Contact(name="홍길동", phone="010-1234-5678", email="hong@example.com")
        card = ContactCard(
            contact=contact,
            on_edit=lambda c: edit_contact(c),
            on_delete=lambda c: delete_contact(c)
        )
        layout.addWidget(card.get_widget())
    """

    edit_clicked = Signal(object)  # Emits Contact object
    delete_clicked = Signal(object)  # Emits Contact object

    def __init__(self, contact, on_edit: Optional[Callable] = None,
                 on_delete: Optional[Callable] = None):
        super().__init__()
        self.contact = contact
        self.on_edit = on_edit
        self.on_delete = on_delete

        # Keep reference to components to prevent garbage collection
        self.card = None
        self.button_group = None

    def create(self):
        """Create contact card widget"""
        # Store Card component reference
        self.card = Card(padding=Spacing.MEDIUM)

        # Contact info layout
        info_layout = QVBoxLayout()
        info_layout.setSpacing(Spacing.XSMALL)

        # Name
        name_label = Label(self.contact.name, variant="heading")
        info_layout.addWidget(name_label.get_widget())

        # Phone
        phone_label = Label(f"📞 {self.contact.phone}", variant="normal")
        info_layout.addWidget(phone_label.get_widget())

        # Email
        email_label = Label(f"📧 {self.contact.email}", variant="normal")
        info_layout.addWidget(email_label.get_widget())

        # Add info to card
        info_widget = QWidget()
        info_widget.setLayout(info_layout)
        self.card.add_widget(info_widget)

        # Action buttons (keep reference to prevent GC)
        edit_btn_config = {
            "text": "수정",
            "variant": "secondary",
            "callback": self._handle_edit,
            "min_width": 80
        }

        delete_btn_config = {
            "text": "삭제",
            "variant": "danger",
            "callback": self._handle_delete,
            "min_width": 80
        }

        self.button_group = ButtonGroup([edit_btn_config, delete_btn_config])
        self.card.add_widget(self.button_group.get_widget())

        return self.card.get_widget()

    def _handle_edit(self):
        """Handle edit button click"""
        self.edit_clicked.emit(self.contact)
        if self.on_edit:
            self.on_edit(self.contact)

    def _handle_delete(self):
        """Handle delete button click"""
        self.delete_clicked.emit(self.contact)
        if self.on_delete:
            self.on_delete(self.contact)


class ContactForm(BaseComponent):
    """
    Reusable contact form component

    Form for adding/editing contacts with validation.

    Usage:
        form = ContactForm(
            on_submit=lambda values: add_contact(values),
            on_clear=lambda: refresh_ui()
        )
        layout.addWidget(form.get_widget())

        # Get form values
        values = form.get_values()  # Returns dict with name, phone, email

        # Populate form
        form.populate(name="홍길동", phone="010-1234-5678", email="hong@example.com")

        # Clear form
        form.clear()
    """

    submitted = Signal(dict)  # Emits dict with name, phone, email
    cleared = Signal()

    def __init__(self, on_submit: Optional[Callable] = None,
                 on_clear: Optional[Callable] = None, title: str = "새 연락처 추가"):
        super().__init__()
        self.on_submit = on_submit
        self.on_clear = on_clear
        self.title = title

        # Form fields (will be created in create())
        self.name_field = None
        self.phone_field = None
        self.email_field = None

        # Keep reference to Card component to prevent garbage collection
        self.form_card = None

    def create(self):
        """Create contact form widget"""
        # Store Card component reference to prevent garbage collection
        self.form_card = Card(title=self.title)

        # Name field
        self.name_field = FormField(
            "이름",
            placeholder="홍길동",
            required=True
        )
        self.form_card.add_component(self.name_field)

        # Phone field
        self.phone_field = FormField(
            "전화번호",
            placeholder="010-1234-5678",
            required=True
        )
        self.form_card.add_component(self.phone_field)

        # Email field with validation
        def validate_email(value):
            if "@" not in value or "." not in value:
                return False, "올바른 이메일 형식이 아닙니다"
            return True, ""

        self.email_field = FormField(
            "이메일",
            placeholder="example@email.com",
            required=True,
            validator=validate_email,
            help_text="연락 가능한 이메일 주소를 입력하세요"
        )
        self.form_card.add_component(self.email_field)

        # Buttons (keep reference to prevent GC)
        add_btn_config = {
            "text": "추가",
            "variant": "success",
            "callback": self._handle_submit,
            "min_width": 100
        }

        clear_btn_config = {
            "text": "초기화",
            "variant": "secondary",
            "callback": self._handle_clear,
            "min_width": 100
        }

        self.button_group = ButtonGroup([add_btn_config, clear_btn_config])
        self.form_card.add_widget(self.button_group.get_widget())

        return self.form_card.get_widget()

    def _handle_submit(self):
        """Handle form submission"""
        # Validate all fields
        if not self.validate():
            return

        values = self.get_values()
        self.submitted.emit(values)

        if self.on_submit:
            self.on_submit(values)

    def _handle_clear(self):
        """Handle clear button"""
        self.clear()
        self.cleared.emit()

        if self.on_clear:
            self.on_clear()

    def validate(self) -> bool:
        """Validate all form fields"""
        fields = [self.name_field, self.phone_field, self.email_field]
        return all(field.validate() for field in fields)

    def get_values(self) -> dict:
        """Get form values as dictionary"""
        return {
            "name": self.name_field.get_value(),
            "phone": self.phone_field.get_value(),
            "email": self.email_field.get_value()
        }

    def populate(self, name: str = "", phone: str = "", email: str = ""):
        """Populate form with values"""
        self.name_field.set_value(name)
        self.phone_field.set_value(phone)
        self.email_field.set_value(email)

    def clear(self):
        """Clear all form fields"""
        self.name_field.set_value("")
        self.phone_field.set_value("")
        self.email_field.set_value("")
        self.name_field.clear_error()
        self.phone_field.clear_error()
        self.email_field.clear_error()


class ContactSearchBar(BaseComponent):
    """
    Reusable contact search bar component

    Search input with real-time filtering.

    Usage:
        search = ContactSearchBar(
            on_search=lambda query: filter_contacts(query)
        )
        layout.addWidget(search.get_widget())

        # Get current search query
        query = search.get_query()

        # Clear search
        search.clear()
    """

    search_changed = Signal(str)  # Emits search query

    def __init__(self, on_search: Optional[Callable] = None,
                 placeholder: str = "이름, 전화번호, 이메일로 검색..."):
        super().__init__()
        self.on_search = on_search
        self.placeholder = placeholder

        # Keep references to components to prevent garbage collection
        self.search_card = None
        self.search_input = None

    def create(self):
        """Create search bar widget"""
        # Store Card component reference
        self.search_card = Card()

        # Search input (keep Input component reference)
        self.search_input = Input(placeholder=self.placeholder)
        self.search_input.textChanged.connect(self._handle_search)

        self.search_card.add_widget(self.search_input.get_widget())

        return self.search_card.get_widget()

    def _handle_search(self, query: str):
        """Handle search input changes"""
        self.search_changed.emit(query)

        if self.on_search:
            self.on_search(query)

    def get_query(self) -> str:
        """Get current search query"""
        return self.search_input.get_value()

    def clear(self):
        """Clear search input"""
        self.search_input.set_value("")
