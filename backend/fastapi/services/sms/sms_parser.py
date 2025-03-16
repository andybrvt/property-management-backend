import logging
from fastapi import Request
from typing import Union, Tuple


logger = logging.getLogger(__name__)

async def parse_incoming_sms(request: Request) -> Union[Tuple[str, str, None], Tuple[str, None, str]]:
    """Parses incoming SMS/MMS from Twilio webhook.
    
    Returns:
        - If it's an SMS: (from_number, message_body, None)
        - If it's an MMS: (from_number, None, media_url)
    """
    try:
        form_data = await request.form()
        from_number = form_data.get("From", "").strip()
        message_body = form_data.get("Body", "").strip()
        num_media = int(form_data.get("NumMedia", 0))

        # ✅ If it's an MMS (image sent)
        if num_media > 0:
            media_url = form_data.get("MediaUrl0")  # First image attached
            logger.info(f"📸 Incoming MMS from {from_number}: {media_url}")
            return from_number, None, media_url

        # ✅ If it's a regular SMS (text)
        logger.info(f"📩 Incoming SMS from {from_number}: {message_body}")
        return from_number, message_body, None

    except Exception as e:
        logger.error(f"❌ Error parsing incoming SMS/MMS: {e}")
        return None, None, None