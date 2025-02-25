from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os
from dotenv import load_dotenv
import re
# Load environment variables
load_dotenv()

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def format_phone_number(phone_number: str) -> str:
    """Ensure phone number is in +1XXXXXXXXXX format (US only)."""

    # Remove all non-numeric characters
    cleaned_number = re.sub(r"\D", "", phone_number)

    # Ensure it's exactly 10 digits (without country code)
    if len(cleaned_number) == 10:
        return f"+1{cleaned_number}"
    # If it starts with "1" and is 11 digits, assume it's a US number
    elif len(cleaned_number) == 11 and cleaned_number.startswith("1"):
        return f"+{cleaned_number}"
    else:
        return None  

def send_sms(to_number: str, message_text: str) -> dict:
    """Send an SMS using Twilio and handle errors."""
    try:
        message = client.messages.create(
            body=message_text,
            from_=TWILIO_PHONE_NUMBER,
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
