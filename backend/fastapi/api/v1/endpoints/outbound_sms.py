from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.fastapi.dependencies.database import get_sync_db
from backend.fastapi.services.lead_service import get_or_create_lead
from backend.fastapi.services.sms_service import send_sms, format_phone_number
from backend.fastapi.services.message_service import store_message_log

router = APIRouter()

@router.post("/start")
def start_lead_conversation(phone_number: str, db: Session = Depends(get_sync_db)):
    """Starts a conversation with a new lead or exits if lead exists."""

    # ✅ Format and validate phone number
    formatted_number = format_phone_number(phone_number)
    if not formatted_number:
        raise HTTPException(
            status_code=400,
            detail="Invalid phone number. Must be a valid 10-digit US number."
        )

    # ✅ Check if lead already exists (no creation)
    lead, error = get_or_create_lead(db, formatted_number, create_new=False)
    if lead:
        return {"message": "Lead already exists. No action taken.", "phone_number": formatted_number}
    
    # ✅ Create new lead
    lead, error = get_or_create_lead(db, formatted_number, create_new=True)
    if error:
        raise HTTPException(status_code=400, detail=f"Error creating lead: {error}")

    # ✅ First message (customizable or replace with AI-generated later)
    first_message = "Hey, thank you for reaching out. We are from XX and it seems like you were interested in one of our properties?"

    # ✅ Send SMS
    result = send_sms(formatted_number, first_message)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error_message"])

    # ✅ Log the outbound message
    store_message_log(db, formatted_number, "outbound", first_message, lead_id=lead.id)

    return {"message": "Conversation started", "phone_number": formatted_number}
