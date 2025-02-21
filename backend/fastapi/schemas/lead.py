from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LeadBase(BaseModel):
    name: str
    email: str
    phone: str
    income: str
    has_pets: bool
    rental_history: Optional[str] = None
    status: str

class LeadCreate(LeadBase):
    pass

class LeadUpdate(LeadBase):
    status: Optional[str] = None

class Lead(LeadBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 