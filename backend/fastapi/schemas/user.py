from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional
from datetime import datetime, timezone
from pydantic import Field


# ✅ Base schema with common fields
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None  # ✅ Make optional
    last_name: Optional[str] = None  # ✅ Make optional
    phone: Optional[str] = None
    role: Optional[str] = "owner"  # owner, tenant, admin

# ✅ Schema for creating a new user (includes password)
class UserCreate(UserBase):
    password: str  # Required for user creation

# ✅ Schema for updating user details (allows partial updates)
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None  # Allow password updates

# ✅ Schema for API response (excludes password)
class UserSchema(UserBase):
    id: UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # ✅ Dynamic timestamp
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # ✅ Dynamic timestamp


    class Config:
        from_attributes = True  # ✅ Ensures compatibility with SQLAlchemy models
