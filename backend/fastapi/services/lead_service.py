from sqlalchemy.orm import Session
from backend.fastapi.crud.lead import get_lead_by_phone, create_lead
from backend.fastapi.services.sms_service import format_phone_number
import logging
from datetime import datetime
from backend.fastapi.constants.lead_statuses import LEAD_STATUSES
from backend.fastapi.models.lead import Lead
from backend.fastapi.services.email_service import send_verification_email
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
    ("showing_scheduled", ["name", "property_interest", "id_verified", "scheduled_showing_date"]),
    ("id_verified", ["name", "property_interest", "id_verified"]),  # ✅ ID must be uploaded before verification
    ("id_verification_requested", ["name", "property_interest"]),  # ✅ If we have name + property, request ID
    ("new", []),  # ✅ Default for leads with no attached info
]

# ✅ Special checks for non-standard fields
SPECIAL_FIELD_CHECKS = {
    "property_interest": lambda lead: len(lead.property_interest) > 0,
    "id_verified": lambda lead: lead.id_verified or bool(lead.driver_license_url),  # ✅ Accepts `id_verified = true`
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

            # ✅ If status becomes "id_verification_requested", send the email
            if status == "id_verification_requested":
                logging.info(f"📸 Requesting ID verification via SMS for Lead {lead.id}")

            break


def update_lead_with_mms(db: Session, lead: Lead, s3_url: str):
    """
    Updates a lead with the uploaded driver's license S3 URL and timestamp.

    Parameters:
    - db (Session): SQLAlchemy DB session.
    - lead (Lead): Lead object to update.
    - s3_url (str): The uploaded image URL.

    Returns:
    - None
    """
    try:
        lead.driver_license_url = s3_url
        lead.driver_license_uploaded_at = datetime.utcnow()
        db.commit()
        logger.info(f"✅ Updated lead {lead.id} with driver license: {s3_url}")
        update_lead_id_verified(db, lead, is_verified=True)


    except Exception as e:
        logger.error(f"❌ Error updating Lead {lead.id} with MMS: {e}")


def update_lead_id_verified(db: Session, lead: Lead, is_verified: bool = True):
    """
    Updates the lead's ID verification status and changes the lead's status to "id_verified".

    Parameters:
    - db (Session): SQLAlchemy DB session.
    - lead (Lead): Lead object to update.
    - is_verified (bool): Whether the ID is verified (default: True).

    Returns:
    - None
    """
    try:
        lead.id_verified = is_verified
        lead.id_verification_date = datetime.utcnow() if is_verified else None
        lead.status = "id_verified" 

        db.commit()
        logger.info(f"✅ Lead {lead.id} ID verification updated: {is_verified}, Status set to: {lead.status}")

    except Exception as e:
        logger.error(f"❌ Error updating Lead {lead.id} ID verification: {e}")
