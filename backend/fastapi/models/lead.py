from sqlalchemy import Column, Integer, String, Boolean, DateTime, UUID, ARRAY, JSON
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from backend.fastapi.dependencies.database import Base
from backend.fastapi.models.meeting import Meeting  


class Lead(Base):
    __tablename__ = 'leads'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=True)  # Can be null initially
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True)  # Phone number from SMS
    income = Column(Integer, nullable=True)  # Monthly income for qualifying
    has_pets = Column(Boolean, default=False)
    rented_before = Column(Boolean, default=False)
    property_interest = Column(String, nullable=True)  # Type of property interested in
    status = Column(String, default="new")  # new, qualified, unqualified
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contact = Column(DateTime, default=datetime.utcnow)
    conversation_state = Column(String, default="initial")  # Track where we are in the conversation
    missing_info = Column(ARRAY(String), default=[])

    # Relationships
    messages = relationship("Message", back_populates="lead")
    meetings = relationship("Meeting", back_populates="lead")

    def __repr__(self):
        return f"<Lead(id={self.id}, name={self.name}, phone={self.phone})>"
