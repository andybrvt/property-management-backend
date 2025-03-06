from sqlalchemy.orm import Session
from backend.fastapi.crud.lead import get_lead_by_phone, create_lead
from backend.fastapi.services.sms_service import format_phone_number
import logging
from backend.fastapi.constants.lead_statuses import LEAD_STATUSES
from backend.fastapi.models.lead import Lead
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


def update_lead_status(db: Session, lead: Lead, new_status: str):
    """Safely updates the lead's status if valid and commits the change."""
    
    if new_status not in LEAD_STATUSES:
        logger.error(f"❌ Invalid status '{new_status}' for Lead {lead.id}")
        return False  # Optionally raise an error instead

    logger.info(f"🔄 Updating Lead {lead.id} status: {lead.status} → {new_status}")
    
    lead.status = new_status
    db.commit()
    db.refresh(lead)
    return True

# ✅ Define the required fields for each status (stacked correctly)
STATUS_RULES = [
    ("showing_scheduled", ["name", "property_interest", "email", "id_verified", "scheduled_showing_date"]),
    ("id_verified", ["name", "property_interest", "email", "id_verified"]),
    ("id_verification_requested", ["name", "property_interest", "email"]),
    ("interested_in_showing", ["name", "property_interest"]),
    ("new", []),  # Fallback
]

# ✅ Special checks for non-standard fields
SPECIAL_FIELD_CHECKS = {
    "property_interest": lambda lead: len(lead.property_interest) > 0,
}

# ✅ Universal field checker
def check_field(lead, field):
    if field in SPECIAL_FIELD_CHECKS:
        return SPECIAL_FIELD_CHECKS[field](lead)
    return getattr(lead, field) not in (None, "", False)

# ✅ Status updater function
def update_lead_status_based_on_info(db: Session, lead: Lead):
    for status, required_fields in STATUS_RULES:
        if all(check_field(lead, field) for field in required_fields):
            lead.status = status
            db.commit()
            db.refresh(lead)
            logging.info(f"✅ Lead {lead.id} status updated to '{status}'")

            break

