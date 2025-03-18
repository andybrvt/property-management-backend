from pydantic import BaseModel, Field, UUID4, constr
from datetime import datetime, date
from typing import Optional


class PropertyBase(BaseModel):
    """Base schema for property data"""
    address: str
    city: str
    state: constr(min_length=2, max_length=2)  # Ensure state is a valid 2-letter code
    zip_code: constr(min_length=5, max_length=10)  # Allow 5-digit or ZIP+4 format
    num_bedrooms: int
    num_bathrooms: int
    sqft: Optional[int] = None
    rent_price: int
    status: str = Field(default="available")  # Can be "available", "occupied", "under maintenance"
    calendly_link: Optional[str] = None  # ✅ Add this field

    # 🔹 New Fields
    property_type: Optional[str] = None  # ✅ "Townhouse", "Apartment", etc.
    lease_duration: Optional[str] = None  # ✅ Example: "12 months"
    available_date: Optional[date] = None  # ✅ Move-in availability date
    landlord_pays: Optional[str] = None  # ✅ What landlord covers (e.g., "HOA, water")
    tenant_pays: Optional[str] = None  # ✅ What tenant covers (e.g., "utilities")
    security_deposit: Optional[int] = None  # ✅ Security deposit amount
    requires_renters_insurance: Optional[bool] = None  # ✅ Does landlord require renters insurance?
    has_laundry: Optional[bool] = None  # ✅ Washer/dryer included?
    cooling_type: Optional[str] = None  # ✅ "Central A/C", "Window Unit", etc.
    appliances: Optional[str] = None  # ✅ "Dishwasher, Microwave, Oven, Fridge"
    parking_type: Optional[str] = None  # ✅ "Detached garage", "Street parking"
    outdoor_features: Optional[str] = None  # ✅ "Balcony, Patio, Backyard"
    allows_pets: Optional[bool] = None  # ✅ Does the property allow pets?
    pet_policy_notes: Optional[str] = None  # ✅ Additional pet rules


    # 🔹 **New Secure Entry Code Field**
    door_code: Optional[str] = None  # ✅ Entry code for property access


class PropertyCreate(PropertyBase):
    """Schema for creating a property"""
    owner_id: UUID4  # Required during creation


class PropertyUpdate(BaseModel):
    """Schema for updating property details"""
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[constr(min_length=2, max_length=2)] = None
    zip_code: Optional[constr(min_length=5, max_length=10)] = None
    num_bedrooms: Optional[int] = None
    num_bathrooms: Optional[int] = None
    sqft: Optional[int] = None
    rent_price: Optional[int] = None
    status: Optional[str] = None
    calendly_link: Optional[str] = None  # ✅ Add this field

    # 🔹 New Fields (Optional Updates)
    property_type: Optional[str] = None
    lease_duration: Optional[str] = None
    available_date: Optional[date] = None
    landlord_pays: Optional[str] = None
    tenant_pays: Optional[str] = None
    security_deposit: Optional[int] = None
    requires_renters_insurance: Optional[bool] = None
    has_laundry: Optional[bool] = None
    cooling_type: Optional[str] = None
    appliances: Optional[str] = None
    parking_type: Optional[str] = None
    outdoor_features: Optional[str] = None
    allows_pets: Optional[bool] = None
    pet_policy_notes: Optional[str] = None

    # 🔹 **New Secure Entry Code Field**
    door_code: Optional[str] = None  # ✅ Allow updates to door code


    class Config:
        from_attributes = True  # ✅ Ensures compatibility with SQLAlchemy ORM


class PropertyResponse(PropertyBase):
    """Response schema for returning a property"""
    id: UUID4
    owner_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # ✅ Allows SQLAlchemy ORM integration


class PropertyDropdownResponse(BaseModel):
    """Minimal property response for dropdown selection"""
    id: str
    address: str  # Only return the ID + address

    class Config:
        from_attributes = True
