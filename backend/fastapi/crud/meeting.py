from sqlalchemy.orm import Session
from uuid import UUID
from backend.fastapi.models.meeting import Meeting
from backend.fastapi.schemas.meeting import MeetingCreate

# Create a new meeting
def create_meeting(db: Session, meeting: MeetingCreate, lead_id: UUID):
    db_meeting = Meeting(lead_id=lead_id, **meeting.dict())
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting

# Get a meeting by ID
def get_meeting(db: Session, meeting_id: UUID):
    return db.query(Meeting).filter(Meeting.id == meeting_id).first()

# Get all meetings for a lead
def get_meetings_for_lead(db: Session, lead_id: UUID, skip: int = 0, limit: int = 10):
    return db.query(Meeting).filter(Meeting.lead_id == lead_id).offset(skip).limit(limit).all()
