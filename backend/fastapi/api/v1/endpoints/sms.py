from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.fastapi.dependencies.database import get_sync_db
from backend.fastapi.crud.lead import get_lead_by_phone, get_or_create_lead
from backend.fastapi.crud.message import store_message_log
from backend.fastapi.services.sms_service import send_sms, format_phone_number
from backend.fastapi.services.ai_service import generate_ai_message
import logging

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

    # ✅ Format phone number (Twilio already sends in correct format)
    formatted_number = from_number  
    logger.info(f"📞 Formatted Phone: {formatted_number}")

    # ✅ Find or create lead
    try:
        lead = get_or_create_lead(db, formatted_number, create_new=True)
        is_new_lead = lead.status == "new"

        logger.info(f"🆔 Lead found/created: {lead.id} | New Lead: {is_new_lead}")

    except Exception as e:
        logger.error(f"❌ Error retrieving or creating lead: {e}")
        return {"status": "error", "message": "Lead lookup failed"}

    # ✅ Store incoming message (Tenant Message)
    store_message_log(db, formatted_number, "incoming", message_body)

    # ✅ Generate AI response (context logic handled inside `generate_ai_message`)
    context = "opening" if is_new_lead else "follow_up"
    ai_response = generate_ai_message(db, lead.id, context, lead)

    # ✅ Send AI-generated message
    send_sms(formatted_number, ai_response)

    return {
        "message": "Reply received and AI response sent",
        "phone_number": formatted_number,
        "lead_id": lead.id
    }


'''
@router.post("/webhook/sms")
def receive_sms(request: Request, db: Session = Depends(get_sync_db)):
    """Handles incoming SMS messages from Twilio"""
    
    form_data = request.form()
    from_number = form_data.get("From", "").strip()
    message_body = form_data.get("Body", "").strip()

    # ✅ Format phone number
    formatted_number = format_phone_number(from_number)
    if not formatted_number:
        raise HTTPException(status_code=400, detail="Invalid phone number format.")

    # ✅ Find existing lead
    lead = get_lead_by_phone(db, formatted_number)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    # ✅ Store incoming message
    store_message_log(db, formatted_number, "incoming", message_body)

    # ✅ AI generates a follow-up response based on conversation context
    ai_response = generate_ai_message("follow_up", lead)

    # ✅ Send AI-generated follow-up SMS
    send_sms(formatted_number, ai_response)

    # ✅ Log AI-generated response
    store_message_log(db, formatted_number, "outgoing", ai_response)

    return {"message": "Reply received and AI follow-up sent", "phone_number": formatted_number}

'''

