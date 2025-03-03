import logging
from fastapi import Request

logger = logging.getLogger(__name__)

async def parse_incoming_sms(request: Request) -> tuple[str, str] | tuple[None, None]:
    """Parses incoming SMS from Twilio webhook."""
    try:
        form_data = await request.form()
        from_number = form_data.get("From", "").strip()
        message_body = form_data.get("Body", "").strip()
        logger.info(f"📩 Incoming SMS from {from_number}: {message_body}")
        return from_number, message_body
    except Exception as e:
        logger.error(f"❌ Error parsing incoming SMS: {e}")
        return None, None
