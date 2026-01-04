"""
Base API schema with automatic camelCase serialization.

This module provides the base model class for all API schemas.
All field names in Python use snake_case, but JSON output uses camelCase
automatically via Pydantic's alias_generator.
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class APIBaseModel(BaseModel):
    """Base model for all API schemas with camelCase JSON serialization.

    Features:
        - Use snake_case for field names in Python code
        - JSON output automatically uses camelCase via alias_generator
        - populate_by_name allows both snake_case and camelCase for input
        - from_attributes enables ORM model conversion

    Example:
        class UserInfo(APIBaseModel):
            user_name: str      # Python: user_name, JSON: "userName"
            email_address: str  # Python: email_address, JSON: "emailAddress"
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
