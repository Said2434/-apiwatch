"""
Pydantic schemas for authentication requests and responses.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """Schema for user registration request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123"
            }
        }


class UserLogin(BaseModel):
    """Schema for user login request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123"
            }
        }


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    """Schema for decoded token data."""
    email: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "created_at": "2024-01-15T10:30:00"
            }
        }
