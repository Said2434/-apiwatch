"""
Pydantic schemas for API monitor requests and responses.
"""
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, Dict
from app.models.api_monitor import HTTPMethod


class MonitorCreate(BaseModel):
    """Schema for creating a new API monitor."""
    name: str = Field(..., min_length=1, max_length=255, description="Monitor name")
    url: str = Field(..., description="API endpoint URL to monitor")
    method: HTTPMethod = Field(default=HTTPMethod.GET, description="HTTP method")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Custom HTTP headers")
    expected_status: int = Field(default=200, ge=100, le=599, description="Expected HTTP status code")
    check_interval: int = Field(default=60, ge=10, le=3600, description="Check interval in seconds (10-3600)")
    timeout: int = Field(default=10, ge=1, le=60, description="Request timeout in seconds (1-60)")
    is_active: bool = Field(default=True, description="Enable/disable monitoring")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Production API",
                "url": "https://api.example.com/health",
                "method": "GET",
                "headers": {"Authorization": "Bearer token123"},
                "expected_status": 200,
                "check_interval": 60,
                "timeout": 10,
                "is_active": True
            }
        }


class MonitorUpdate(BaseModel):
    """Schema for updating an existing API monitor."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    url: Optional[str] = None
    method: Optional[HTTPMethod] = None
    headers: Optional[Dict[str, str]] = None
    expected_status: Optional[int] = Field(None, ge=100, le=599)
    check_interval: Optional[int] = Field(None, ge=10, le=3600)
    timeout: Optional[int] = Field(None, ge=1, le=60)
    is_active: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated API Name",
                "check_interval": 120,
                "is_active": False
            }
        }


class MonitorResponse(BaseModel):
    """Schema for API monitor in responses."""
    id: int
    user_id: int
    name: str
    url: str
    method: HTTPMethod
    headers: Optional[Dict[str, str]]
    expected_status: int
    check_interval: int
    timeout: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "name": "Production API",
                "url": "https://api.example.com/health",
                "method": "GET",
                "headers": {"Authorization": "Bearer token123"},
                "expected_status": 200,
                "check_interval": 60,
                "timeout": 10,
                "is_active": True,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": None
            }
        }


class MonitorListResponse(BaseModel):
    """Schema for paginated monitor list response."""
    total: int
    monitors: list[MonitorResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "total": 2,
                "monitors": [
                    {
                        "id": 1,
                        "user_id": 1,
                        "name": "Production API",
                        "url": "https://api.example.com/health",
                        "method": "GET",
                        "headers": None,
                        "expected_status": 200,
                        "check_interval": 60,
                        "timeout": 10,
                        "is_active": True,
                        "created_at": "2024-01-15T10:30:00",
                        "updated_at": None
                    }
                ]
            }
        }
