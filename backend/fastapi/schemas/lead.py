from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class LeadBase(BaseModel):
    name: str
    email: str
    phone: str
    income: Optional[int] = None
    has_pets: bool = False
    rented_before: bool = False
    status: Optional[str] = "new"

class LeadCreate(LeadBase):
    pass  # Additional validation if needed when creating a lead

class LeadUpdate(LeadBase):
    status: Optional[str] = None
    income: Optional[int] = None

class Lead(LeadBase):
    id: UUID
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True  # This tells Pydantic to work with SQLAlchemy models
