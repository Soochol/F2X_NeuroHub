from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from app.models.refresh_token import RefreshToken
from app.core import security


def create_refresh_token(
    db: Session, *, user_id: int, expires_delta: timedelta
) -> RefreshToken:
    """Create a new refresh token for a user."""
    token_str = security.create_refresh_token()
    expires_at = datetime.now(timezone.utc) + expires_delta
    
    db_obj = RefreshToken(
        token=token_str,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
    """Get a refresh token by its string value."""
    result = db.execute(select(RefreshToken).where(RefreshToken.token == token))
    return result.scalar_one_or_none()


def revoke_refresh_token(db: Session, token: str) -> None:
    """Revoke (delete) a refresh token."""
    db.execute(delete(RefreshToken).where(RefreshToken.token == token))
    db.commit()


def revoke_all_user_tokens(db: Session, user_id: int) -> None:
    """Revoke all refresh tokens for a specific user."""
    db.execute(delete(RefreshToken).where(RefreshToken.user_id == user_id))
    db.commit()


def is_refresh_token_valid(token_obj: RefreshToken) -> bool:
    """Check if a refresh token is valid (not expired and not revoked)."""
    if token_obj.revoked_at:
        return False
    return token_obj.expires_at > datetime.now(timezone.utc)
