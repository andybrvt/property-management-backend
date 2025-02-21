from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MeetingBase(BaseModel):
    scheduled_time: datetime
    duration: int
    location: str
    meeting_type: str
    status: str
    notes: Optional[str] = None

class MeetingCreate(MeetingBase):
    lead_id: int

class Meeting(MeetingBase):
    id: int
    lead_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 