import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from backend.fastapi.models.lead import Lead
# ✅ Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Load your SendGrid API key
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "YOUR-API-KEY-HERE")
FROM_EMAIL = "andybrvt@gmail.com"  # Update this to your verified sender email

def send_email(to_email: str, subject: str, body: str):
    """Send an email via SendGrid."""
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"📧 Email sent to {to_email} (Status: {response.status_code})")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send email to {to_email}: {e}")
        return False

FRONTEND_URL = "https://yourfrontend.com"

def send_verification_email(lead: Lead):
    verification_link = f"{FRONTEND_URL}/upload-id/{lead.id}"

    subject = "Action Required: Verify Your ID to Move Forward"
    body = f"""
    Hi {lead.name or 'there'},

    Thanks for your interest in scheduling a showing! Before we can move forward, please upload a photo of your government-issued ID.

    ✅ Upload your ID here:
    {verification_link}

    Once we receive your ID, we’ll send you a link to schedule your showing.

    Let us know if you have any questions!

    Thanks,  
    Your Leasing Team
    """

    send_email(
        to_email=lead.email,
        subject=subject,
        body=body
    )
