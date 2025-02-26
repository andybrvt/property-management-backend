from sqlalchemy.orm import Session
from backend.fastapi.models.message import Message
from typing import Dict, Any, List
from uuid import UUID
from typing import Optional  
from datetime import datetime, timedelta, timezone
from backend.fastapi.models.message import Message
import uuid


'''
# Create a new message from dictionary data (async)
async def create_message_dict_async(db: Session, message_data: Dict[str, Any]) -> Message:
    """Create a new message asynchronously"""
    db_message = Message(**message_data)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

'''


def get_or_create_session(db: Session, lead_id: int, time_window: int = 10):
    """
    Finds an existing message session within the time window, or creates a new session.
    """
    recent_message = (
        db.query(Message)
        .filter(Message.lead_id == lead_id)
        .filter(Message.sent_at >= datetime.now(timezone.utc) - timedelta(seconds=time_window))
        .order_by(Message.sent_at.desc())
        .first()
    )

    if recent_message and recent_message.session_id:
        return recent_message.session_id  # ✅ Reuse existing session
    else:
        return uuid.uuid4()  # ✅ Create new session if none exists

def store_message_log(db: Session, phone_number: str, direction: str, message: str, lead_id: UUID = None, session_id: UUID = None):
    """Logs a message sent or received into the Messages table with session tracking and lead_id."""
    
    msg_entry = Message(
        phone_number=phone_number,
        direction=direction,
        content=message,
        lead_id=lead_id,  # ✅ Ensure lead_id is stored properly
        session_id=session_id,  # ✅ Store session ID
        sent_at=datetime.now(timezone.utc)  # ✅ Ensure timestamp is stored
    )
    
    db.add(msg_entry)
    db.commit()

def get_last_messages(db: Session, lead_id: int, limit: int = 3):
    """
    Fetches the last 'limit' messages for a given lead, sorted by newest first.
    Returns a list of messages with role indicators (tenant or AI).
    """
    messages = (
        db.query(Message)
        .filter(Message.lead_id == lead_id)
        .order_by(Message.sent_at.desc())  # ✅ FIXED: Use 'sent_at' instead of 'created_at'
        .limit(limit)
        .all()
    )

    return [
        {"role": "assistant" if msg.is_ai_generated else "tenant", "text": msg.content}
        for msg in reversed(messages)  # Reverse to maintain conversation order
    ]

def save_ai_message(db: Session, lead_id: int, message_text: str):
    """
    Saves an AI-generated message in the Messages table.
    """
    ai_message = Message(
        lead_id=lead_id,
        content=message_text,
        direction="outgoing",
        is_ai_generated=True,  # ✅ Mark it as AI-generated
        status="sent"
    )
    db.add(ai_message)
    db.commit()
    return ai_message


# Create a new message from dictionary data (sync)
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

# Get all messages for a lead (with pagination)
def get_messages_for_lead(db: Session, lead_id: UUID, skip: int = 0, limit: int = 10) -> List[Message]:
    """Get all messages for a lead with pagination"""
    return db.query(Message).filter(Message.lead_id == lead_id).offset(skip).limit(limit).all()

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
