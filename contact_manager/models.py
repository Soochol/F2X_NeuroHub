"""
Contact Model

Data class for contact information.
"""

from dataclasses import dataclass
from typing import Optional
import uuid


@dataclass
class Contact:
    """Contact data class"""
    name: str
    phone: str
    email: str
    id: str = None

    def __post_init__(self):
        """Generate ID if not provided"""
        if self.id is None:
            self.id = str(uuid.uuid4())

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Contact':
        """Create Contact from dictionary"""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            phone=data.get("phone", ""),
            email=data.get("email", "")
        )

    def matches_search(self, query: str) -> bool:
        """Check if contact matches search query"""
        query = query.lower()
        return (
            query in self.name.lower() or
            query in self.phone.lower() or
            query in self.email.lower()
        )
