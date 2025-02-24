from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from backend.fastapi.dependencies.database import Base

class Meeting(Base):
    __tablename__ = 'meetings'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id'))
    meeting_time = Column(DateTime)  # When the meeting is scheduled
    property_details = Column(String)  # Property info or description for the meeting
    status = Column(String, default="scheduled")  # Status of the meeting (e.g., 'scheduled', 'completed', 'cancelled')

    # Relationship to the Lead model
    #lead = relationship("Lead", back_populates="meetings")

    def __repr__(self):
        return f"<Meeting(id={self.id}, meeting_time={self.meeting_time}, status={self.status})>"
