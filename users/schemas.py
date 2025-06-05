from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user model with common fields."""
    username: str
    email: EmailStr

class UserCreate(UserBase):
    """User creation model with password."""
    password: str

class UserUpdate(UserBase):
    """User update model with optional fields."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    """User response model for API responses."""
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration for UserResponse."""
        from_attributes = True
