"""Health Check model for storing API check results."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class HealthCheck(Base):
    """
    Health Check results table.

    Stores the result of each API health check performed by the background worker.

    Relationships:
        - Belongs to one API monitor
    """
    __tablename__ = "health_checks"

    id = Column(Integer, primary_key=True, index=True)
    monitor_id = Column(
        Integer,
        ForeignKey("api_monitors.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Check Results
    status_code = Column(Integer, nullable=True)  # HTTP status code (null if request failed)
    response_time = Column(Float, nullable=True)  # Response time in milliseconds
    is_up = Column(Boolean, default=False, nullable=False)  # True if check passed
    error_message = Column(String(1024), nullable=True)  # Error details if check failed

    # Timestamp
    checked_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True  # Index for time-based queries
    )

    # Relationships
    monitor = relationship("APIMonitor", back_populates="health_checks")

    # Composite index for efficient queries (get recent checks for a monitor)
    __table_args__ = (
        Index('ix_monitor_checked_at', 'monitor_id', 'checked_at'),
    )

    def __repr__(self):
        return (
            f"<HealthCheck(id={self.id}, monitor_id={self.monitor_id}, "
            f"is_up={self.is_up}, status_code={self.status_code})>"
        )
