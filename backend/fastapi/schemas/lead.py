from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from .property_interest import PropertyInterestResponse  # ✅ import the response schema
from typing import List


class LeadBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: str
    income: Optional[int] = None
    has_pets: bool = False
    rented_before: bool = False
    status: Optional[str] = "new"
    move_in_date: Optional[datetime] = None
    uncertain_interest: bool = True  # ✅ Default to True
    interest_city: Optional[str] = None  # ✅ Optional, no default


class LeadCreate(LeadBase):
    pass  


class LeadUpdate(BaseModel):  
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    income: Optional[int] = None
    has_pets: Optional[bool] = None
    rented_before: Optional[bool] = None
    status: Optional[str] = None
    move_in_date: Optional[datetime] = None
    uncertain_interest: Optional[bool] = None
    interest_city: Optional[str] = None


class LeadSchema(LeadBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    property_interest: List[PropertyInterestResponse] = []
    driver_license_url: Optional[str] = None
    driver_license_uploaded_at: Optional[datetime] = None


    class Config:
        from_attributes = True  

