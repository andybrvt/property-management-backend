from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

class LeadBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None  # ✅ Changed from EmailStr to a regular string to allow flexibility
    phone: str
    income: Optional[int] = None
    has_pets: bool = False
    rented_before: bool = False
    status: Optional[str] = "new"
    move_in_date: Optional[datetime] = None

class LeadCreate(LeadBase):
    pass  

class LeadUpdate(BaseModel):  
    name: Optional[str] = None
    email: Optional[str] = None  # ✅ Same fix here
    phone: Optional[str] = None
    income: Optional[int] = None
    has_pets: Optional[bool] = None
    rented_before: Optional[bool] = None
    status: Optional[str] = None
    move_in_date: Optional[datetime] = None

class LeadSchema(LeadBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  
