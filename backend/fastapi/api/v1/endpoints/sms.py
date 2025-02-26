from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.fastapi.dependencies.database import get_sync_db
from backend.fastapi.crud.lead import get_lead_by_phone, get_or_create_lead
from backend.fastapi.crud.message import store_message_log, get_or_create_session
from backend.fastapi.services.sms_service import send_sms, format_phone_number
from backend.fastapi.services.ai_service import generate_ai_message
import logging
from datetime import datetime, timedelta, timezone
import uuid
from backend.fastapi.models.message import Message
import asyncio


router = APIRouter()

# ✅ Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/webhook/sms")
async def receive_sms(request: Request, db: Session = Depends(get_sync_db)):
    """Handles incoming SMS messages from Twilio. If the sender is not in the lead database, create a new lead."""

    try:
        form_data = await request.form()
        from_number = form_data.get("From", "").strip()
        message_body = form_data.get("Body", "").strip()
        logger.info(f"📩 Incoming SMS from {from_number}: {message_body}")

    except Exception as e:
        logger.error(f"❌ Error parsing incoming SMS: {e}")
        return {"status": "error", "message": "Failed to process request"}

    # ✅ Find or create lead
    try:
        lead = get_or_create_lead(db, from_number, create_new=True)
        is_new_lead = lead.status == "new"
        logger.info(f"🆔 Lead found/created: {lead.id} | New Lead: {is_new_lead}")

    except Exception as e:
        logger.error(f"❌ Error retrieving or creating lead: {e}")
        return {"status": "error", "message": "Lead lookup failed"}

    # ✅ Find or create a message session
    session_id = get_or_create_session(db, lead.id)

    # ✅ Ensure `lead_id` is properly passed when storing the message
    store_message_log(db, from_number, "incoming", message_body, lead_id=lead.id, session_id=session_id)


    # ✅ Wait a few seconds to check for more messages before responding
    cooldown_time = 5  # ⏳ Adjust the wait time if needed
    await asyncio.sleep(cooldown_time)

    # ✅ Check for the **absolute newest message** in the entire database (not just this session)
    absolute_latest_message = (
        db.query(Message)
        .filter(Message.lead_id == lead.id)
        .order_by(Message.sent_at.desc())
        .first()
    )

    # ✅ Get the last message timestamp
    last_message_time = absolute_latest_message.sent_at.replace(tzinfo=timezone.utc) if absolute_latest_message else None
    current_time = datetime.now(timezone.utc)

    # ✅ If **any** new message arrived within the cooldown, exit without responding
    if last_message_time and (current_time - last_message_time).total_seconds() < cooldown_time:
        logger.info("🚨 A newer message arrived! Exiting without responding...")
        return {"status": "waiting", "message": "Newer messages detected, delaying AI response"}

    # ✅ If no new messages arrived, process and respond
    session_messages = (
        db.query(Message)
        .filter(Message.lead_id == lead.id, Message.session_id == session_id)
        .order_by(Message.sent_at.asc())
        .all()
    )

    # ✅ Combine session messages into one text block
    combined_message = " ".join([msg.content for msg in session_messages])

    # ✅ Generate AI response (context handled inside `generate_ai_message`)
    context = "opening" if is_new_lead else "follow_up"
    ai_response = generate_ai_message(db, lead.id, context, lead)

    # ✅ Send AI-generated message
    send_sms(from_number, ai_response)

    return {
        "message": "Reply received and AI response sent",
        "phone_number": from_number,
        "lead_id": lead.id
    }


