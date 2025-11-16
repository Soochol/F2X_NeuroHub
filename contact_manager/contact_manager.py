"""
Contact Manager Main Window

PySide6 GUI application for managing contacts using reusable components.
Demonstrates Skill architecture with custom theme and component library.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QMessageBox, QFrame
)
from PySide6.QtCore import Qt

# Add ui_components to path
UI_COMPONENTS_PATH = Path(__file__).parent.parent / ".claude" / "skills" / "pyqt-pyside-gui" / "scripts"
sys.path.insert(0, str(UI_COMPONENTS_PATH))

from ui_components import load_theme, Button, Label, Spacing

from models import Contact
from storage import ContactStorage
from contact_components import ContactCard, ContactForm, ContactSearchBar


class ContactManager(QMainWindow):
    """Main window for contact manager application"""

    def __init__(self):
        super().__init__()
        self.storage = ContactStorage()
        self.current_theme = "contact-manager"
        self.contact_widgets = {}  # Track contact card widgets
        self.setup_ui()
        self.refresh_contacts()

    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle("연락처 관리")
        self.setGeometry(100, 100, 700, 800)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(Spacing.LARGE)
        layout.setContentsMargins(
            Spacing.LARGE, Spacing.LARGE,
            Spacing.LARGE, Spacing.LARGE
        )

        # Header with title and theme button
        header = self._create_header()
        layout.addWidget(header)

        # Search section (using ContactSearchBar component)
        self.search_bar = ContactSearchBar(on_search=self.on_search)
        layout.addWidget(self.search_bar.get_widget())

        # Add contact form (using ContactForm component)
        self.contact_form = ContactForm(
            on_submit=self.add_contact,
            on_clear=lambda: None  # Clear already handled by component
        )
        layout.addWidget(self.contact_form.get_widget())

        # Contact list section
        self.contacts_scroll = self._create_contacts_section()
        layout.addWidget(self.contacts_scroll, stretch=1)

    def _create_header(self) -> QWidget:
        """Create header with title and theme toggle"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.MEDIUM)

        # Title
        title = Label("📇 연락처 관리", variant="title")
        layout.addWidget(title.get_widget())

        layout.addStretch()

        # Theme toggle button
        self.theme_btn = Button("🌙 Dark", variant="outline", size="small")
        self.theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_btn.get_widget())

        return container

    def _create_contacts_section(self) -> QScrollArea:
        """Create scrollable contacts list section"""
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        # Container for contacts
        self.contacts_container = QWidget()
        self.contacts_layout = QVBoxLayout(self.contacts_container)
        self.contacts_layout.setSpacing(Spacing.MEDIUM)
        self.contacts_layout.setContentsMargins(0, 0, 0, 0)
        self.contacts_layout.addStretch()

        scroll.setWidget(self.contacts_container)

        return scroll

    def refresh_contacts(self, search_query: str = ""):
        """Refresh the contacts list"""
        # Clear existing contact widgets
        while self.contacts_layout.count():
            item = self.contacts_layout.takeAt(0)
            if item.widget():
                widget = item.widget()
                widget.blockSignals(True)
                widget.setParent(None)
                widget.deleteLater()

        self.contact_widgets.clear()

        # Get contacts
        if search_query:
            contacts = self.storage.search(search_query)
        else:
            contacts = self.storage.get_all()

        # Add header
        if contacts:
            header = Label(f"연락처 목록 ({len(contacts)})", variant="heading")
            self.contacts_layout.insertWidget(0, header.get_widget())

            # Add contact cards using ContactCard component
            for i, contact in enumerate(contacts):
                card = ContactCard(
                    contact=contact,
                    on_edit=self.edit_contact,
                    on_delete=self.delete_contact
                )
                card_widget = card.get_widget()
                self.contacts_layout.insertWidget(i + 1, card_widget)
                self.contact_widgets[contact.id] = card_widget
        else:
            # Empty state
            if search_query:
                msg = Label("검색 결과가 없습니다", variant="normal")
            else:
                msg = Label("아직 등록된 연락처가 없습니다\n위 폼에서 새 연락처를 추가하세요", variant="normal")
                msg.get_widget().setAlignment(Qt.AlignCenter)

            self.contacts_layout.insertWidget(0, msg.get_widget())

        # Add stretch at the end
        self.contacts_layout.addStretch()

    def add_contact(self, values: dict):
        """Add new contact"""
        # Create contact from form values
        contact = Contact(
            name=values["name"],
            phone=values["phone"],
            email=values["email"]
        )

        # Save to storage
        self.storage.add(contact)

        # Show success message FIRST (before triggering signals)
        # This prevents modal dialog from processing queued signals prematurely
        QMessageBox.information(
            self,
            "성공",
            f"'{contact.name}' 연락처가 추가되었습니다."
        )

        # Refresh UI (after modal dialog closes)
        self.contact_form.clear()
        self.refresh_contacts()

    def edit_contact(self, contact: Contact):
        """Edit existing contact"""
        # Populate form with contact data
        self.contact_form.populate(
            name=contact.name,
            phone=contact.phone,
            email=contact.email
        )

        # Delete old contact
        self.storage.delete(contact.id)

        # Refresh list
        self.refresh_contacts()

        # Scroll to top
        self.contacts_scroll.verticalScrollBar().setValue(0)

    def delete_contact(self, contact: Contact):
        """Delete contact"""
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "삭제 확인",
            f"'{contact.name}' 연락처를 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.storage.delete(contact.id)
            self.refresh_contacts()
            QMessageBox.information(self, "성공", "연락처가 삭제되었습니다.")

    def on_search(self, query: str):
        """Handle search input"""
        self.refresh_contacts(query)

    def toggle_theme(self):
        """Toggle between contact-manager and dark theme"""
        from PySide6.QtWidgets import QApplication

        if self.current_theme == "contact-manager":
            self.current_theme = "dark"
            self.theme_btn.set_text("☀️ Light")
            load_theme(QApplication.instance(), "dark")
        else:
            self.current_theme = "contact-manager"
            self.theme_btn.set_text("🌙 Dark")
            load_theme(QApplication.instance(), "contact-manager")
