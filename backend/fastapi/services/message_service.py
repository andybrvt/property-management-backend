# services/message_service.py

from sqlalchemy.orm import Session
from backend.fastapi.crud.message import (
    create_message, get_message, get_messages_for_lead,
    get_all_messages, update_message, delete_message, get_messages_by_session
)
from typing import List, Dict
from uuid import UUID
from backend.fastapi.models.message import Message  # SQLAlchemy model
from backend.fastapi.schemas import MessageSchema  # Pydantic schema
from typing import Optional  
from fastapi import HTTPException
import logging
from datetime import datetime, timezone, timedelta
import uuid

def fetch_messages_by_session(db: Session, session_id: str):
    """
    Fetches all messages for a given session.
    Ensures AI services only call this function instead of accessing CRUD directly.
    """
    return get_messages_by_session(db, session_id)  # ✅ Calls the raw CRUD function

def save_ai_message(db: Session, lead_id: int, message_text: str, session_id: str = None):
    """
    Saves an AI-generated message and ensures session tracking.
    """
    session_id = session_id or get_or_create_session(db, lead_id)  # ✅ Generate session ID if not provided

    message_data = {
        "lead_id": lead_id,
        "content": message_text,
        "direction": "outgoing",
        "is_ai_generated": True,
        "status": "sent",
        "session_id": session_id,
    }

    return create_message(db, message_data)  # ✅ Uses `create_message()` to store message

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

def get_last_messages(db: Session, lead_id: int, limit: int = 3):
    """
    Fetches the last 'limit' messages for a given lead, sorted by newest first.
    Used for AI conversation context.
    """
    messages = get_messages_for_lead(db, lead_id, limit=limit)  # ✅ Now correctly ordered!

    return [
        {"role": "assistant" if msg.is_ai_generated else "tenant", "text": msg.content}
        for msg in reversed(messages)  # ✅ Reverse to maintain correct conversation order
    ]

def get_conversation_context(
    db: Session,
    lead_id: int,
    session_id: str,
    limit: int = 10
) -> tuple[list[str], list[str], list[str]]:
    latest_messages = fetch_messages_by_session(db, session_id)
    latest_tenant_messages = [msg.content for msg in latest_messages]

    session_messages = get_last_messages(db, lead_id, limit=limit)
    session_messages = [msg for msg in session_messages if msg["text"] not in latest_tenant_messages]

    tenant_messages = [msg["text"] for msg in session_messages if msg["role"] == "tenant"]
    ai_messages = [msg["text"] for msg in session_messages if msg["role"] == "assistant"]

    return latest_tenant_messages, tenant_messages, ai_messages