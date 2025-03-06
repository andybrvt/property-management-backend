import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

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
