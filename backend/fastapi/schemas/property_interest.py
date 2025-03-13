from pydantic import BaseModel
from uuid import UUID
from datetime import datetime




class PropertyInterestResponse(BaseModel):
    id: UUID
    property_id: UUID
    status: str
    scheduled_showing: bool
    application_submitted: bool
    created_at: datetime

    class Config:
        from_attributes = True
