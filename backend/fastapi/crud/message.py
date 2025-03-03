from sqlalchemy.orm import Session
from backend.fastapi.models.message import Message
from typing import Dict, Any, List
from uuid import UUID
from typing import Optional  
from datetime import datetime, timedelta, timezone
from backend.fastapi.models.message import Message
import uuid





def get_messages_by_session(db: Session, session_id: str):
    """
    Retrieves all messages in a given session, ordered by timestamp.
    """
    return (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.sent_at.asc())
        .all()
    )


def create_message(db: Session, message_data: Dict[str, Any]) -> Message:
    """Create a new message"""
    db_message = Message(**message_data)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

# Get a message by its ID
def get_message(db: Session, message_id: UUID) -> Message:
    """Get a message by ID"""
    return db.query(Message).filter(Message.id == message_id).first()

def get_messages_for_lead(db: Session, lead_id: UUID, skip: int = 0, limit: int = 10) -> List[Message]:
    """Retrieve all messages for a lead, ordered by most recent first (sent_at DESC)."""
    return (
        db.query(Message)
        .filter(Message.lead_id == lead_id)
        .order_by(Message.sent_at.desc())  # ✅ Ensures most recent messages come first
        .offset(skip)
        .limit(limit)
        .all()
    )
def get_all_messages(db: Session, skip: int = 0, limit: int = 10) -> List[Message]:
    """
    Retrieve all messages with pagination, ordered from newest to oldest.
    """
    return (
        db.query(Message)
        .order_by(Message.sent_at.desc())  # ✅ Fetch newest messages first
        .offset(skip)
        .limit(limit)
        .all()
    )

def update_message(db: Session, message_id: UUID, message_data: Dict[str, Any]) -> Optional[Message]:
    """Update an existing message"""
    db_message = db.query(Message).filter(Message.id == message_id).first()
    if db_message:
        for key, value in message_data.items():
            setattr(db_message, key, value)
        db.commit()
        db.refresh(db_message)
        return db_message  # ✅ Return the updated message
    return None  # ✅ Return None if message does not exist

def delete_message(db: Session, message_id: UUID) -> Optional[Message]:
    """Delete a message by its ID"""
    db_message = db.query(Message).filter(Message.id == message_id).first()

    if db_message:
        db.delete(db_message)
        db.commit()
        return db_message  # ✅ Return deleted message
    
    return None  # ✅ Explicitly return None if message not found
