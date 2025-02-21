from sqlalchemy.orm import Session
from models.meeting import Meeting
from schemas.meeting import MeetingCreate

def create_meeting(db: Session, meeting_data: dict):
    db_meeting = Meeting(**meeting_data)
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting

def get_meetings(db: Session, lead_id: int):
    return db.query(Meeting).filter(Meeting.lead_id == lead_id).all()

def get_meeting(db: Session, meeting_id: int):
    return db.query(Meeting).filter(Meeting.id == meeting_id).first()

def update_meeting_status(db: Session, meeting_id: int, status: str):
    db_meeting = get_meeting(db, meeting_id)
    if db_meeting:
        db_meeting.status = status
        db.commit()
        db.refresh(db_meeting)
    return db_meeting 