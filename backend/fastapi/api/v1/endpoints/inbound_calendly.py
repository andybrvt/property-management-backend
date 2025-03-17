from fastapi import APIRouter, HTTPException, Request, Depends
import os
import requests
import json
from pydantic import BaseModel
from datetime import datetime
from backend.fastapi.models.lead import Lead
from backend.fastapi.dependencies.database import get_sync_db
from sqlalchemy.orm import Session
from backend.fastapi.services.sms_service import format_phone_number
from backend.fastapi.services.sms_service import send_sms
from backend.fastapi.services.message_service import save_ai_message
router = APIRouter()

# Load API key from environment variables
CALENDLY_API_KEY = os.getenv("CALENDLY_API_KEY")
ORG_URI = "https://api.calendly.com/organizations/0b883923-6179-4093-9944-4b16efc2d33b"  # Your actual organization ID


class WebhookRequest(BaseModel):
    webhook_url: str

@router.get("/user-info")
def get_calendly_user_info():
    if not CALENDLY_API_KEY:
        raise HTTPException(status_code=500, detail="Calendly API key not found. Check your .env file.")

    headers = {
        "Authorization": f"Bearer {CALENDLY_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get("https://api.calendly.com/users/me", headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Calendly user info: {str(e)}")


@router.post("/webhook")
async def calendly_webhook(request: Request, db: Session = Depends(get_sync_db)):
    payload = await request.json()
    
    # Debugging: Print full payload
    print("📩 Received Calendly Webhook:", json.dumps(payload, indent=4))

    # Extract event type (either "invitee.created" or "invitee.canceled")
    event_type = payload.get("event")
    event_data = payload.get("payload", {})

    # Extract phone number from "questions_and_answers"
    phone_number = None
    for qa in event_data.get("questions_and_answers", []):
        if qa.get("question") == "Phone Number":
            phone_number = qa.get("answer")
            break

    if not phone_number:
        print("⚠️ No phone number found in the payload. Ignoring event.")
        return {"status": "ignored"}

    # Format phone number before searching
    formatted_number = format_phone_number(phone_number)
    print(f"📞 Formatted Phone Number: {formatted_number}")

    # Extract scheduled showing date
    scheduled_event = event_data.get("scheduled_event", {})
    start_time_str = scheduled_event.get("start_time")  # ISO 8601 format: "2025-03-17T14:00:00.000000Z"

    # Convert start_time string to datetime object
    scheduled_date = None
    if start_time_str:
        scheduled_date = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))

    # Find the lead using formatted phone number
    lead = db.query(Lead).filter(Lead.phone == formatted_number).first()

    if not lead:
        print(f"⚠️ No lead found with phone number {formatted_number}. Ignoring event.")
        return {"status": "ignored"}

    # If the lead scheduled a tour, update their status & scheduled date
    if event_type == "invitee.created":
        lead.status = "showing_scheduled"
        lead.scheduled_showing_date = scheduled_date
        db.commit()
        print(f"✅ Lead {lead.name} ({formatted_number}) updated: showing_scheduled at {scheduled_date}")

        ai_message = "Just saw you scheduled, let me know if you need anything else!"
        save_ai_message(db, lead.id, ai_message)
        send_sms(lead.phone, ai_message)



    return {"status": "success", "lead_id": lead.id, "new_status": lead.status}
    



# /api/v1/calendly/webhook

@router.post("/setup-webhook")
def setup_calendly_webhook(request: WebhookRequest):
    """Dynamically register a webhook URL with Calendly."""
    if not CALENDLY_API_KEY:
        raise HTTPException(status_code=500, detail="Calendly API key not found. Check your .env file.")

    headers = {
        "Authorization": f"Bearer {CALENDLY_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "url": request.webhook_url,
        "events": ["invitee.created", "invitee.canceled"],  # Listen for bookings & cancellations
        "organization": ORG_URI,
        "scope": "organization"
    }

    response = requests.post("https://api.calendly.com/webhook_subscriptions", headers=headers, json=data)

    if response.status_code == 201:
        return {"message": "Webhook registered successfully!", "response": response.json()}
    else:
        raise HTTPException(status_code=response.status_code, detail=f"Failed to register webhook: {response.text}")
