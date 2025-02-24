from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class MeetingBase(BaseModel):
    meeting_time: datetime
    property_details: str
    status: Optional[str] = "scheduled"

class MeetingCreate(MeetingBase):
    pass  # Schema for creating a meeting

class Meeting(MeetingBase):
    id: UUID
    lead_id: UUID

    class Config:
        orm_mode = True  # To work with SQLAlchemy models
