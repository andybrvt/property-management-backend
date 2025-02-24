from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

class LeadBase(BaseModel):
    name: str
    email: EmailStr  # ✅ Ensure valid email format
    phone: str
    income: Optional[int] = None
    has_pets: bool = False
    rented_before: bool = False
    status: Optional[str] = "new"

class LeadCreate(LeadBase):
    pass  # ✅ No changes needed for creating a lead

class LeadUpdate(LeadBase):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    income: Optional[int] = None
    has_pets: Optional[bool] = None
    rented_before: Optional[bool] = None
    status: Optional[str] = None

class LeadSchema(LeadBase):
    id: UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # ✅ Fixes timestamp issue
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        from_attributes = True  # ✅ Pydantic v2 way to work with SQLAlchemy
