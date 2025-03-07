import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from backend.fastapi.models.lead import Lead
from backend.fastapi.utils.s3 import s3_client

# ✅ Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Load your SendGrid API key
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "YOUR-API-KEY-HERE")
FROM_EMAIL = "andybrvt@gmail.com"  # Update this to your verified sender email

def send_email(to_email: str, subject: str, body: str, html_body: str = None):
    """Send an email via SendGrid with optional HTML support."""
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body,
        html_content=html_body or body  # Fallback to plain text if no HTML provided
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"📧 Email sent to {to_email} (Status: {response.status_code})")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send email to {to_email}: {e}")
        return False

FRONTEND_URL = "https://property-management-frontend-bay.vercel.app"

def send_verification_email(lead: Lead):
    verification_link = f"{FRONTEND_URL}/upload-id/{lead.id}"

    subject = "Action Required: Verify Your ID to Move Forward"

    # Plain text body (for email clients that don’t support HTML)
    body = f"""
    Hi {lead.name or 'there'},

    Thanks for your interest in scheduling a showing! Before we can move forward, please upload a photo of your government-issued ID.

    Upload your ID here:
    {verification_link}

    Once we receive your ID, we’ll send you a link to schedule your showing.

    Let us know if you have any questions!

    Thanks,  
    Your Leasing Team
    """

    # HTML body (clean, with hyperlink)
    html_body = f"""
    <p>Hi {lead.name or 'there'},</p>

    <p>Thanks for your interest in scheduling a showing! Before we can move forward, please upload a photo of your government-issued ID.</p>

    <p>✅ <a href="{verification_link}" target="_blank">Click here to upload your ID</a></p>

    <p>Once we receive your ID, we’ll send you a link to schedule your showing.</p>

    <p>Let us know if you have any questions!</p>

    <p>Thanks,<br>Your Leasing Team</p>
    """

    send_email(
        to_email=lead.email,
        subject=subject,
        body=body,
        html_body=html_body
    )


def send_operator_id_notification(lead: Lead):
    """
    Sends an email to the operator with a pre-signed URL to download the uploaded ID.
    """
    if not lead.driver_license_url:
        logger.error(f"❌ No driver_license_url found for Lead {lead.id}")
        return False

    # Extract the object key from the full S3 URL
    file_key = lead.driver_license_url.split(".amazonaws.com/")[-1]

    try:
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': os.getenv('AWS_S3_BUCKET_NAME'),
                'Key': file_key,
                'ResponseContentDisposition': 'attachment'
            },
            ExpiresIn=3600  # Link valid for 1 hour
        )
    except Exception as e:
        logger.error(f"❌ Failed to generate pre-signed URL for Lead {lead.id}: {e}")
        return False

    subject = f"📄 New ID Uploaded: {lead.name or 'Unknown Lead'}"

    body = f"""
    Hey team,

    {lead.name or 'A lead'} just uploaded their ID.

    Lead Info:
    - Name: {lead.name}
    - Phone: {lead.phone}
    - Email: {lead.email}

    ✅ Download the ID (link expires in 1 hour):
    {presigned_url}

    Thanks,  
    Your Leasing Assistant
    """

    html_body = f"""
    <p>Hey team,</p>

    <p>{lead.name or 'A lead'} just uploaded their ID.</p>

    <p><strong>Lead Info:</strong><br>
    - Name: {lead.name}<br>
    - Phone: {lead.phone}<br>
    - Email: {lead.email}</p>

    <p>✅ <a href="{presigned_url}" target="_blank">Download the ID</a> (link expires in 1 hour)</p>

    <p>Thanks,<br>Your Leasing Assistant</p>
    """

    return send_email(
        to_email="andybrvt@gmail.com",  # Replace with your real operator email
        subject=subject,
        body=body,
        html_body=html_body
    )

