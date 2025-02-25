from sqlalchemy.orm import Session
from backend.fastapi.models.message import Message
from typing import Dict, Any, List
from uuid import UUID
from typing import Optional  


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

def store_message_log(db: Session, phone_number: str, direction: str, message: str):
    """Logs a message sent or received into the Messages table."""
    msg_entry = Message(phone_number=phone_number, direction=direction, content=message)
    db.add(msg_entry)
    db.commit()



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

# Get all messages (without lead-specific filtering)
def get_all_messages(db: Session, skip: int = 0, limit: int = 10) -> List[Message]:
    """Retrieve all messages with pagination"""
    return db.query(Message).offset(skip).limit(limit).all()

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
