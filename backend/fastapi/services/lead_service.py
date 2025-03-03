from sqlalchemy.orm import Session
from backend.fastapi.crud.lead import get_lead_by_phone, create_lead
from backend.fastapi.services.sms_service import format_phone_number
import logging

# ✅ Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_lead_by_phone(db: Session, phone_number: str):
    """Finds a lead by phone number, handles validation & logging."""
    
    # ✅ Log the lookup request
    logger.info(f"🔍 Looking for lead with phone: {phone_number}")

    # ✅ Call the DB query function from `lead_crud.py`
    lead = get_lead_by_phone(db, phone_number)

    if lead:
        logger.info(f"✅ Lead found: {lead.id} for phone {phone_number}")
        return lead, None  # ✅ Standardized return (lead, error)

    logger.warning(f"❌ No lead found for phone {phone_number}")
    return None, "Lead not found"


def get_or_create_lead(db: Session, phone_number: str, **extra_fields):
    """Retrieve an existing lead by phone number or create a new one if not found.

    - Ensures phone number is properly formatted.
    - Calls `lead_crud.py` to execute DB queries.
    - Handles logging, validation, and optional extra fields.
    """

    # ✅ Step 1: Format the phone number
    formatted_number = format_phone_number(phone_number)
    if not formatted_number:
        return None, "Invalid phone number format"

    # ✅ Step 2: Try to find the lead
    lead = get_lead_by_phone(db, formatted_number)
    if lead:
        logger.info(f"✅ Lead found: {lead.id} for phone {formatted_number}")
        return lead, None  # ✅ Return lead if found

    # ✅ Step 3: If lead doesn't exist, create a new one with optional fields
    try:
        lead = create_lead(db, formatted_number, **extra_fields)
        logger.info(f"🎉 New lead created: {lead.id} for phone {formatted_number}")
        return lead, None

    except Exception as e:
        logger.error(f"❌ Error creating lead for {formatted_number}: {e}")
        return None, "Error creating lead"
