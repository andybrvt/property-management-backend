from fastapi import APIRouter, HTTPException, Request, Response
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os
from dotenv import load_dotenv
from schemas.sms import SMSRequest, SMSResponse
from twilio.twiml.messaging_response import MessagingResponse

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

@router.post("/webhook/sms/")
async def receive_sms(request: Request):
    """Endpoint to receive SMS messages from Twilio webhook"""
    form_data = await request.form()
    message_body = form_data.get("Body", "").strip().lower()
    from_number = form_data.get("From", "")
    
    # Validate and format the phone number
    if not from_number:
        return {"status": "error", "message": "No phone number provided"}
    
    # Remove any spaces or special characters except +
    cleaned_number = ''.join(char for char in from_number if char.isdigit() or char == '+')
    
    # Ensure number starts with +1
    if not cleaned_number.startswith('+1'):
        if cleaned_number.startswith('1'):
            cleaned_number = '+' + cleaned_number
        elif cleaned_number.startswith('+'):
            cleaned_number = '+1' + cleaned_number[1:]
        else:
            cleaned_number = '+1' + cleaned_number
    
    # Validate the length (should be 12 characters including +1 and 10 digits)
    if len(cleaned_number) != 12:
        return {"status": "error", "message": "Invalid phone number length"}
    
    # Prepare response message based on incoming text
    response_text = "Thanks for your message! This is an automated response."
    if "hello" in message_body:
        response_text = "Hi there! Thanks for reaching out!"
    elif "help" in message_body:
        response_text = "How can I assist you today?"
    
    # Use existing send_sms function to send the response
    result = await send_sms(
        to_number=cleaned_number,
        message_text=response_text
    )
    
    return {"status": "success", "response": result} 


