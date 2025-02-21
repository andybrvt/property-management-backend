from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SMSMessageBase(BaseModel):
    direction: str
    content: str
    status: str
    from_number: str
    to_number: str
    twilio_sid: Optional[str] = None

class SMSMessageCreate(SMSMessageBase):
    lead_id: int

class SMSMessage(SMSMessageBase):
    id: int
    lead_id: int
    created_at: datetime

    class Config:
        orm_mode = True 