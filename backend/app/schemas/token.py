from typing import Optional, Any
from pydantic import BaseModel, Field


class Token(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Optional[dict[str, Any]] = None


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""
    sub: Optional[str] = None
    role: Optional[str] = None
    username: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str = Field(..., description="The refresh token string")
    station_id: Optional[str] = Field(
        None,
        description="Station ID for station API key refresh (optional)",
    )
