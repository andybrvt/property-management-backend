from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.fastapi.dependencies.database import get_sync_db
from backend.fastapi.crud.lead import get_lead_by_phone
from backend.fastapi.services.lead_service import get_or_create_lead
from backend.fastapi.services.lead_service import find_lead_by_phone
from backend.fastapi.services.message_service import get_or_create_session
from backend.fastapi.services.message_service import store_message_log
from backend.fastapi.services.sms_service import send_sms, format_phone_number
from backend.fastapi.services.ai_service import generate_ai_message
import logging
from datetime import datetime, timedelta, timezone
import uuid
from backend.fastapi.models.message import Message
import asyncio
from backend.fastapi.services.sms.sms_parser import parse_incoming_sms
from backend.fastapi.services.message.message_checker import wait_and_check_new_messages

router = APIRouter()

# ✅ Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/webhook/sms")
async def receive_sms(request: Request, db: Session = Depends(get_sync_db)):
    """Handles incoming SMS messages from Twilio. If the sender is not in the lead database, create a new lead."""

    from_number, message_body = await parse_incoming_sms(request)
    if not from_number or not message_body:
        return {"status": "error", "message": "Failed to process request"}
   
     # ✅ Find or create lead (now properly unpacking the return value)
    lead, error = get_or_create_lead(db, from_number)
    
    if error:
        logger.error(f"❌ Error retrieving or creating lead: {error}")
        return {"status": "error", "message": error}

    is_new_lead = lead.status == "new"
    logger.info(f"🆔 Lead found/created: {lead.id} | New Lead: {is_new_lead}")

    # ✅ Find or create a message session
    session_id = get_or_create_session(db, lead.id)

    # ✅ Store the received message with `session_id`
    store_message_log(db, from_number, "incoming", message_body, lead_id=lead.id, session_id=session_id)

    if await wait_and_check_new_messages(db, lead.id):
        return {"status": "waiting", "message": "Newer messages detected, delaying AI response"}

    # ✅ Generate AI response using the full session conversation
    context = "opening" if is_new_lead else "follow_up"
    ai_response = generate_ai_message(db, lead.id, session_id, context, lead)

    # ✅ Send AI-generated message
    send_sms(from_number, ai_response)

    return {
        "message": "Reply received and AI response sent",
        "phone_number": from_number,
        "lead_id": lead.id
    }


