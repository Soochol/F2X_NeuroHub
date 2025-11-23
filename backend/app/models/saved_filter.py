from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, JSONBDict

class SavedFilter(Base):
    """
    Stores user-defined filter configurations for reuse.
    """
    __tablename__ = "saved_filters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Serialized filter configuration (e.g., list of field/operator/value)
    filters: Mapped[dict] = mapped_column(JSONBDict, nullable=False, default=dict)
    
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="saved_filters")

# Type hint imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
