from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FollowUpBase(BaseModel):
    follow_up_type: str
    scheduled_date: datetime
    status: str
    notes: Optional[str] = None

class FollowUpCreate(FollowUpBase):
    lead_id: int

class FollowUp(FollowUpBase):
    id: int
    lead_id: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True 