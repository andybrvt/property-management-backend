from sqlalchemy.orm import Session
from models.follow_up import FollowUp
from schemas.follow_up import FollowUpCreate
from datetime import datetime

def create_follow_up(db: Session, follow_up_data: dict):
    db_follow_up = FollowUp(**follow_up_data)
    db.add(db_follow_up)
    db.commit()
    db.refresh(db_follow_up)
    return db_follow_up

def get_follow_ups(db: Session, lead_id: int):
    return db.query(FollowUp).filter(FollowUp.lead_id == lead_id).all()

def get_follow_up(db: Session, follow_up_id: int):
    return db.query(FollowUp).filter(FollowUp.id == follow_up_id).first()

def complete_follow_up(db: Session, follow_up_id: int):
    db_follow_up = get_follow_up(db, follow_up_id)
    if db_follow_up:
        db_follow_up.status = 'completed'
        db_follow_up.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(db_follow_up)
    return db_follow_up 