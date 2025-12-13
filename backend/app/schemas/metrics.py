"""
Pydantic schemas for metrics and statistics.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class HealthCheckResponse(BaseModel):
    """Schema for health check result."""
    id: int
    monitor_id: int
    status_code: Optional[int]
    response_time: Optional[float]
    is_up: bool
    error_message: Optional[str]
    checked_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "monitor_id": 1,
                "status_code": 200,
                "response_time": 145.32,
                "is_up": True,
                "error_message": None,
                "checked_at": "2024-01-15T10:30:00"
            }
        }


class HealthCheckListResponse(BaseModel):
    """Schema for paginated health check list."""
    total: int
    health_checks: List[HealthCheckResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "health_checks": [
                    {
                        "id": 1,
                        "monitor_id": 1,
                        "status_code": 200,
                        "response_time": 145.32,
                        "is_up": True,
                        "error_message": None,
                        "checked_at": "2024-01-15T10:30:00"
                    }
                ]
            }
        }


class IncidentResponse(BaseModel):
    """Schema for incident data."""
    id: int
    monitor_id: int
    started_at: datetime
    resolved_at: Optional[datetime]
    duration: Optional[int]
    alert_sent: bool

    @property
    def is_ongoing(self) -> bool:
        """Check if incident is still ongoing."""
        return self.resolved_at is None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "monitor_id": 1,
                "started_at": "2024-01-15T10:00:00",
                "resolved_at": "2024-01-15T10:05:00",
                "duration": 300,
                "alert_sent": True
            }
        }


class IncidentListResponse(BaseModel):
    """Schema for paginated incident list."""
    total: int
    incidents: List[IncidentResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "total": 5,
                "incidents": []
            }
        }


class MonitorStats(BaseModel):
    """Statistics for a single monitor."""
    monitor_id: int
    monitor_name: str
    total_checks: int
    successful_checks: int
    failed_checks: int
    uptime_percentage: float = Field(..., description="Uptime percentage (0-100)")
    avg_response_time: Optional[float] = Field(None, description="Average response time in ms")
    last_check_at: Optional[datetime]
    last_check_status: Optional[bool]
    total_incidents: int
    ongoing_incidents: int

    class Config:
        json_schema_extra = {
            "example": {
                "monitor_id": 1,
                "monitor_name": "Production API",
                "total_checks": 1440,
                "successful_checks": 1435,
                "failed_checks": 5,
                "uptime_percentage": 99.65,
                "avg_response_time": 156.8,
                "last_check_at": "2024-01-15T10:30:00",
                "last_check_status": True,
                "total_incidents": 2,
                "ongoing_incidents": 0
            }
        }


class DashboardStats(BaseModel):
    """Overall dashboard statistics."""
    total_monitors: int
    active_monitors: int
    inactive_monitors: int
    total_incidents: int
    ongoing_incidents: int
    overall_uptime: float = Field(..., description="Overall uptime percentage")
    monitors: List[MonitorStats]

    class Config:
        json_schema_extra = {
            "example": {
                "total_monitors": 5,
                "active_monitors": 4,
                "inactive_monitors": 1,
                "total_incidents": 10,
                "ongoing_incidents": 1,
                "overall_uptime": 98.5,
                "monitors": []
            }
        }
