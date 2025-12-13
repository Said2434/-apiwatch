"""Incident model for tracking downtime periods."""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Incident(Base):
    """
    Incident table for tracking downtime periods.

    An incident represents a period when an API was down (consecutive failed health checks).

    Lifecycle:
        1. Created when first health check fails
        2. Updated with each failed check
        3. Closed (resolved_at set) when health check succeeds again

    Relationships:
        - Belongs to one API monitor
    """
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    monitor_id = Column(
        Integer,
        ForeignKey("api_monitors.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Incident Timeline
    started_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    resolved_at = Column(DateTime(timezone=True), nullable=True)  # Null if still ongoing

    # Duration in seconds (calculated when resolved)
    duration = Column(Integer, nullable=True)

    # Alert tracking
    alert_sent = Column(Boolean, default=False, nullable=False)

    # Relationships
    monitor = relationship("APIMonitor", back_populates="incidents")

    @property
    def is_resolved(self) -> bool:
        """Check if incident is resolved."""
        return self.resolved_at is not None

    @property
    def is_ongoing(self) -> bool:
        """Check if incident is still ongoing."""
        return self.resolved_at is None

    def __repr__(self):
        status = "resolved" if self.is_resolved else "ongoing"
        return (
            f"<Incident(id={self.id}, monitor_id={self.monitor_id}, "
            f"status={status}, started_at={self.started_at})>"
        )
