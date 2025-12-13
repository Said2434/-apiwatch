"""User model for authentication and authorization."""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """
    User table for authentication.

    Relationships:
        - One user can have many API monitors
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    api_monitors = relationship(
        "APIMonitor",
        back_populates="user",
        cascade="all, delete-orphan"  # Delete monitors when user is deleted
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
