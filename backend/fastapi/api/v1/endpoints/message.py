from typing import List
from uuid import UUID
from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.fastapi.dependencies.database import get_sync_db
from backend.fastapi.schemas import MessageBase, MessageCreate, MessageSchema
from backend.fastapi.services.message_service import (
    create_message, get_message, get_all_messages,
    update_message, delete_message
)
from backend.fastapi.services.ai.ai_prompts import build_ai_message_history
from backend.fastapi.services.ai.lead_info_checker import get_missing_lead_info
from backend.fastapi.services.message_service import get_conversation_context
from backend.fastapi.crud.lead import get_lead
from backend.fastapi.services.ai.openai_client import call_openai_chat
import logging
from backend.fastapi.services.email_service import send_email

router = APIRouter()


# ✅ Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/test-ai-message/{lead_id}")
def test_ai_message_build(
    lead_id: UUID,
    db: Session = Depends(get_sync_db)
):
    """
    Test building the full AI message payload for a lead.
    """
    # Get the lead
    lead = get_lead(db, lead_id)
    if not lead:
        return {"error": "Lead not found."}

    # Get conversation history
    conversation_history = get_conversation_context(
        db, lead_id,
        limit=15
    )

    # Get missing info question
    missing_info_question = get_missing_lead_info(lead)

    # Build full message payload
    messages = build_ai_message_history(
        conversation_history,
        missing_info_question
    )

    # ✅ Log full messages to check for bad data
    for i, message in enumerate(messages):
        if not message.get("content"):
            logging.warning(f"⚠️ Message #{i} has empty content: {message}")
        else:
            logging.info(f"✅ Message #{i}: {message}")

    # 🧠 Generate the AI reply
    ai_message = call_openai_chat(messages, max_tokens=120)

    if not ai_message:
        return {"error": "Failed to generate AI message."}


    return {
        "lead_id": str(lead_id),
        "current_status": lead.status,
        "missing_info_question": missing_info_question,
        "messages_payload": messages, 
        "generated_ai_message": ai_message
    }


@router.post("/test-send-email")
def test_send_email(
    db: Session = Depends(get_sync_db)
):
    """Test sending an email via SendGrid."""
    test_email = "andybrvt@gmail.com"  # ⬅️ Replace with your own test email
    subject = "Test Email from Leasing Assistant"
    body = """
Hi there,

This is a test email from the Leasing Assistant system. 🎉

If you're seeing this, the email service is working perfectly!

Thanks,
Your AI Leasing Team
"""

    success = send_email(test_email, subject, body)

    if success:
        return {"message": f"✅ Test email sent to {test_email}"}
    else:
        raise HTTPException(status_code=500, detail="❌ Failed to send test email.")



# Create a message
@router.post("/messages/", response_model=MessageSchema, status_code=status.HTTP_201_CREATED)
def create_message_endpoint(message_data: MessageCreate, db: Session = Depends(get_sync_db)):
    return create_message(db, message_data.model_dump())  # ✅ Uses direct function call

# Get all messages
@router.get("/messages/", response_model=List[MessageSchema], status_code=status.HTTP_200_OK)
def get_messages(skip: int = 0, limit: int = 30, db: Session = Depends(get_sync_db)):
    return get_all_messages(db, skip, limit)  # ✅ Uses direct function call

# Get a single message
@router.get("/messages/{message_id}", response_model=MessageSchema, status_code=status.HTTP_200_OK)
def get_message_endpoint(message_id: UUID, db: Session = Depends(get_sync_db)):
    message = get_message(db, message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

# Update message
@router.put("/messages/{message_id}", response_model=MessageSchema, status_code=status.HTTP_200_OK)
def update_message_endpoint(message_id: UUID, message_data: MessageBase, db: Session = Depends(get_sync_db)):
    return update_message(db, message_id, message_data.model_dump())

# Delete message
@router.delete("/messages/{message_id}", response_model=MessageSchema, status_code=status.HTTP_200_OK)
def delete_message_endpoint(message_id: UUID, db: Session = Depends(get_sync_db)):
    return delete_message(db, message_id)
