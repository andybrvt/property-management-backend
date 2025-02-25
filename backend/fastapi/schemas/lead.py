from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

class LeadBase(BaseModel):
    name: Optional[str] = None  # ✅ Now allows NULL values
    email: Optional[EmailStr] = None  # ✅ Now allows NULL values
    phone: str
    income: Optional[int] = None
    has_pets: bool = False
    rented_before: bool = False
    status: Optional[str] = "new"

class LeadCreate(LeadBase):
    pass  # ✅ No changes needed for creating a lead

class LeadUpdate(BaseModel):  # ✅ Now allows partial updates
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    income: Optional[int] = None
    has_pets: Optional[bool] = None
    rented_before: Optional[bool] = None
    status: Optional[str] = None

class LeadSchema(LeadBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # ✅ Pydantic v2 way to work with SQLAlchemy
