"""
Contact Storage

JSON-based storage for contacts with CRUD operations.
"""

import json
import os
from typing import List, Optional
from pathlib import Path

from models import Contact


class ContactStorage:
    """Manages contact storage in JSON file"""

    def __init__(self, filename: str = "contacts.json"):
        """Initialize storage with filename"""
        self.filename = Path(__file__).parent / filename
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create empty JSON file if it doesn't exist"""
        if not self.filename.exists():
            self._save_data({"contacts": []})

    def _load_data(self) -> dict:
        """Load data from JSON file"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"contacts": []}

    def _save_data(self, data: dict):
        """Save data to JSON file"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_all(self) -> List[Contact]:
        """Get all contacts"""
        data = self._load_data()
        return [Contact.from_dict(c) for c in data.get("contacts", [])]

    def add(self, contact: Contact) -> Contact:
        """Add new contact"""
        data = self._load_data()
        contacts = data.get("contacts", [])
        contacts.append(contact.to_dict())
        data["contacts"] = contacts
        self._save_data(data)
        return contact

    def update(self, contact: Contact) -> bool:
        """Update existing contact"""
        data = self._load_data()
        contacts = data.get("contacts", [])

        for i, c in enumerate(contacts):
            if c.get("id") == contact.id:
                contacts[i] = contact.to_dict()
                data["contacts"] = contacts
                self._save_data(data)
                return True

        return False

    def delete(self, contact_id: str) -> bool:
        """Delete contact by ID"""
        data = self._load_data()
        contacts = data.get("contacts", [])
        original_len = len(contacts)

        contacts = [c for c in contacts if c.get("id") != contact_id]

        if len(contacts) < original_len:
            data["contacts"] = contacts
            self._save_data(data)
            return True

        return False

    def search(self, query: str) -> List[Contact]:
        """Search contacts by name, phone, or email"""
        all_contacts = self.get_all()
        if not query:
            return all_contacts

        return [c for c in all_contacts if c.matches_search(query)]

    def get_by_id(self, contact_id: str) -> Optional[Contact]:
        """Get contact by ID"""
        all_contacts = self.get_all()
        for contact in all_contacts:
            if contact.id == contact_id:
                return contact
        return None
