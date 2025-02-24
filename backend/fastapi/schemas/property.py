from pydantic import BaseModel, Field, UUID4, constr
from datetime import datetime
from typing import Optional


class PropertyBase(BaseModel):
    address: str
    city: str
    state: constr(min_length=2, max_length=2)  # Ensure state is a valid 2-letter code
    zip_code: constr(min_length=5, max_length=10)  # Allow 5-digit or ZIP+4 format
    num_bedrooms: int
    num_bathrooms: int
    sqft: Optional[int] = None
    rent_price: int
    status: str = Field(default="available")  # Can be available, occupied, under maintenance


class PropertyCreate(PropertyBase):
    owner_id: UUID4  # Required during creation


class PropertyUpdate(BaseModel):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[constr(min_length=2, max_length=2)] = None
    zip_code: Optional[constr(min_length=5, max_length=10)] = None
    num_bedrooms: Optional[int] = None
    num_bathrooms: Optional[int] = None
    sqft: Optional[int] = None
    rent_price: Optional[int] = None
    status: Optional[str] = None


class PropertyResponse(PropertyBase):
    id: UUID4
    owner_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # ✅ Allows SQLAlchemy ORM integration
