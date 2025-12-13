"""API Monitor model for tracking monitored endpoints."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class HTTPMethod(str, enum.Enum):
    """Supported HTTP methods for API monitoring."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class APIMonitor(Base):
    """
    API Monitor configuration table.

    Each monitor represents an API endpoint to be checked periodically.

    Relationships:
        - Belongs to one user
        - Has many health checks
        - Has many incidents
    """
    __tablename__ = "api_monitors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Monitor Configuration
    name = Column(String(255), nullable=False)  # e.g., "Production API"
    url = Column(String(2048), nullable=False)  # API endpoint URL
    method = Column(Enum(HTTPMethod), default=HTTPMethod.GET, nullable=False)
    headers = Column(JSON, default=dict)  # Custom headers as JSON
    expected_status = Column(Integer, default=200, nullable=False)  # Expected HTTP status code

    # Check Settings
    check_interval = Column(Integer, default=60, nullable=False)  # Seconds between checks
    timeout = Column(Integer, default=10, nullable=False)  # Request timeout in seconds
    is_active = Column(Boolean, default=True, nullable=False)  # Enable/disable monitoring

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="api_monitors")
    health_checks = relationship(
        "HealthCheck",
        back_populates="monitor",
        cascade="all, delete-orphan",
        order_by="HealthCheck.checked_at.desc()"
    )
    incidents = relationship(
        "Incident",
        back_populates="monitor",
        cascade="all, delete-orphan",
        order_by="Incident.started_at.desc()"
    )

    def __repr__(self):
        return f"<APIMonitor(id={self.id}, name={self.name}, url={self.url})>"
