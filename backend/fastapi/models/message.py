import uuid
from sqlalchemy import Column, String, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from backend.fastapi.dependencies.database import Base
from backend.fastapi.models.lead import Lead  


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True)
    content = Column(Text, nullable=False)  # Message content
    direction = Column(String, nullable=True, default="incoming")  # Default to 'incoming'
    phone_number = Column(String, nullable=True, default="")  # Ensure phone number is never None
    twilio_sid = Column(String, nullable=True)  # Twilio message ID
    status = Column(String, default="pending")  # pending, sent, delivered, failed
    sent_at = Column(DateTime, nullable=True, default=lambda: datetime.now(timezone.utc))  # Ensure sent_at is never None
    is_ai_generated = Column(Boolean, nullable=True, default=False)  # ✅ New field


    # Relationship to Lead
    lead = relationship("Lead", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, direction={self.direction}, status={self.status})>"
