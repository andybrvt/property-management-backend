from fastapi import APIRouter, HTTPException, Request, Response, Depends
from sqlalchemy.orm import Session
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os
from dotenv import load_dotenv
from schemas.sms import SMSRequest, SMSResponse
from datetime import datetime
from backend.fastapi.dependencies.database import get_sync_db
from backend.fastapi.crud import lead as lead_crud
from backend.fastapi.crud import message as message_crud
from backend.fastapi.services.openai_service import generate_response
#from backend.fastapi.models.lead import LeadCreate
import json
import openai

# Load environment variables
load_dotenv()

router = APIRouter()

async def send_sms(to_number: str, message_text: str) -> dict:
    """Send SMS using Twilio client"""
    client = Client(
        os.getenv("TWILIO_ACCOUNT_SID"),
        os.getenv("TWILIO_AUTH_TOKEN")
    )
    
    try:
        message = client.messages.create(
            body=message_text,
            from_="+14809990455",
            to=to_number
        )
        
        return {
            "status": "success",
            "message_sid": message.sid,
            "error_message": None
        }
        
    except TwilioRestException as e:
        return {
            "status": "error",
            "message_sid": None,
            "error_message": f"Twilio error: {str(e.msg)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message_sid": None,
            "error_message": f"Unexpected error: {str(e)}"
        }

@router.post("/send_sms/", response_model=SMSResponse)
async def send_sms_endpoint(sms_request: SMSRequest):
    """Endpoint to send SMS messages"""
    result = await send_sms(
        to_number=sms_request.to_number,
        message_text=sms_request.message_text
    )
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=400,
            detail=result["error_message"]
        )
    
    return result

async def analyze_message_for_lead_info(message: str) -> dict:
    """Use LLM to extract lead information from message"""
    prompt = f"""
    Extract relevant lead information from this message: "{message}"
    Look for:
    - Name
    - Income
    - Has pets (yes/no)
    - Rental history
    - Property interest
    - Email address
    
    Return only the found information in JSON format.
    """
    
    response = await openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        return json.loads(response.choices[0].message.content)
    except:
        return {}

@router.post("/webhook/sms/")
async def receive_sms(request: Request, db: Session = Depends(get_sync_db)):
    """Handle incoming SMS messages from Twilio webhook"""
    form_data = await request.form()
    
    # Get message details from Twilio
    from_number = form_data.get("From", "")
    message_body = form_data.get("Body", "").strip()
    message_sid = form_data.get("MessageSid", "")
    
    # Clean phone number
    cleaned_number = ''.join(char for char in from_number if char.isdigit() or char == '+')
    if not cleaned_number.startswith('+1'):
        cleaned_number = '+1' + cleaned_number.lstrip('1')
    
    # Find or create lead
    lead = lead_crud.get_lead_by_phone(db, cleaned_number)
    is_first_message = False
    
    if not lead:
        is_first_message = True
        lead = lead_crud.create_lead(db, LeadCreate(
            phone=cleaned_number,
            status="new"
        ))
    
    # Store incoming message
    incoming_message = message_crud.create_message(db, {
        "lead_id": lead.id,
        "content": message_body,
        "direction": "incoming",
        "phone_number": cleaned_number,
        "twilio_sid": message_sid,
        "status": "received"
    })
    
    # Analyze message for lead information
    lead_info = await analyze_message_for_lead_info(message_body)
    
    # Update lead with any new information
    update_data = {}
    if lead_info.get('name') and not lead.name:
        update_data['name'] = lead_info['name']
    if lead_info.get('income') and not lead.income:
        update_data['income'] = lead_info['income']
    if lead_info.get('has_pets') is not None and not lead.has_pets:
        update_data['has_pets'] = lead_info['has_pets']
    if lead_info.get('property_interest') and not lead.property_interest:
        update_data['property_interest'] = lead_info['property_interest']
    
    # Update lead if new information found
    if update_data:
        lead = lead_crud.update_lead(db, lead.id, update_data)
    
    # Generate AI response
    ai_response = await generate_response(
        lead=lead,
        message=message_body,
        context_data={
            "conversation_state": lead.conversation_state,
            "last_contact": lead.last_contact,
            "status": lead.status
        }
    )
    
    # Send response via Twilio
    client = Client(
        os.getenv("TWILIO_ACCOUNT_SID"),
        os.getenv("TWILIO_AUTH_TOKEN")
    )
    
    try:
        twilio_message = client.messages.create(
            body=ai_response,
            from_="+14809990455",  # Your Twilio number
            to=cleaned_number
        )
        
        # Store outgoing message
        outgoing_message = message_crud.create_message(db, {
            "lead_id": lead.id,
            "content": ai_response,
            "direction": "outgoing",
            "phone_number": cleaned_number,
            "twilio_sid": twilio_message.sid,
            "status": "sent"
        })
        
        # Update lead's last contact time
        lead_crud.update_lead(db, lead.id, {"last_contact": datetime.utcnow()})
        
        return {
            "status": "success",
            "lead_id": str(lead.id),
            "incoming_message_id": str(incoming_message.id),
            "outgoing_message_id": str(outgoing_message.id)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@router.post("/test/ai-response/")
async def test_ai_response():
    """Test endpoint to verify OpenAI connection and response generation"""
    try:
        # Test basic OpenAI connection
        test_response = await openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello!"}
            ],
            max_tokens=50
        )
        
        # Create a mock lead for testing
        mock_lead = Lead(
            name="Test User",
            phone="+15202483488",
            income=5000,
            has_pets=True,
            property_interest="apartment"
        )
        
        # Test your generate_response function
        ai_response = await generate_response(
            lead=mock_lead,
            message="I'm interested in a 2-bedroom apartment",
            context_data={
                "conversation_state": "initial",
                "last_contact": datetime.utcnow(),
                "status": "new"
            }
        )
        
        return {
            "status": "success",
            "openai_test": test_response.choices[0].message.content,
            "generate_response_test": ai_response,
            "api_key_configured": bool(os.getenv("OPENAI_API_KEY"))
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "api_key_configured": bool(os.getenv("OPENAI_API_KEY"))
        }


