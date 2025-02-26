from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime, timezone

class MessageBase(BaseModel):
    content: str
    direction: Optional[str] = "incoming"  # Default to 'incoming' to avoid validation errors
    phone_number: Optional[str] = None  # Ensure phone number is never None
    status: Optional[str] = "pending"
    twilio_sid: Optional[str] = None
    is_ai_generated: Optional[bool] = False  # ✅ Added this field
    session_id: Optional[UUID] = None  # ✅ NEW FIELD: Tracks conversation sessions

class MessageCreate(MessageBase):
    lead_id: Optional[UUID] = None  # Allow lead_id to be missing if not required

class MessageSchema(MessageBase):
    id: UUID
    lead_id: Optional[UUID] = None  # Allow messages without a lead_id
    sent_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))  # Proper default handling

    class Config:
        from_attributes = True  # Ensures compatibility with SQLAlchemy models

class Message(MessageSchema):
    pass  # For backwards compatibility if needed
