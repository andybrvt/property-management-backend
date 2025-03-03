from datetime import datetime
import logging
from backend.fastapi.models.lead import Lead
import re
from sqlalchemy.orm import Session

def is_valid_email(email: str) -> bool:
    """Returns True if the email is valid and not empty, otherwise False."""
    if not email or email.strip() == "":  # Ignore empty strings
        return False
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(email_regex, email))

def update_lead_with_extracted_info(db: Session, lead: Lead, extracted_info: dict) -> bool:
    updated = False

    if "name" in extracted_info and not lead.name:
        lead.name = extracted_info["name"]
        updated = True
    if "move_in_date" in extracted_info and not lead.move_in_date:
        try:
            lead.move_in_date = datetime.strptime(extracted_info["move_in_date"], "%Y-%m-%d")
            updated = True
        except ValueError:
            logging.error(f"❌ Invalid date format: {extracted_info['move_in_date']}")
    if "income" in extracted_info and (lead.income is None or lead.income == 0):
        try:
            lead.income = int(extracted_info["income"])
            updated = True
        except ValueError:
            logging.error(f"❌ Invalid income format: {extracted_info['income']}")
    if "has_pets" in extracted_info and lead.has_pets is None:
        lead.has_pets = bool(extracted_info["has_pets"])
        updated = True
    if "rented_before" in extracted_info and lead.rented_before is None:
        lead.rented_before = bool(extracted_info["rented_before"])
        updated = True
    if "property_interest" in extracted_info and not lead.property_interest:
        lead.property_interest = extracted_info["property_interest"]
        updated = True
    if "email" in extracted_info:
        email_value = extracted_info["email"].strip()
        if is_valid_email(email_value):
            lead.email = email_value
            updated = True
        else:
            logging.warning(f"⚠️ Skipping invalid or empty email: '{email_value}'")

    if updated:
        db.commit()
        logging.info(f"✅ Updated Lead {lead.id} with extracted details")

    return updated
