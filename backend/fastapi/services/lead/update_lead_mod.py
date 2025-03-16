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

    if name := extracted_info.get("name"):
        if not lead.name:
            logging.info(f"🔍 Updating Lead {lead.id} with name: {name}")
            lead.name = name.strip()
            updated = True

    if move_in_date_str := extracted_info.get("move_in_date"):
        if not lead.move_in_date and move_in_date_str.strip():
            try:
                lead.move_in_date = datetime.strptime(move_in_date_str, "%Y-%m-%d")
                updated = True
            except ValueError:
                logging.error(f"❌ Invalid date format: {move_in_date_str}")

    if income_str := extracted_info.get("income"):
        if (lead.total_income is None or lead.total_income == 0) and income_str.strip():
            try:
                lead.total_income = int(income_str)
                updated = True
            except ValueError:
                logging.error(f"❌ Invalid income format: {income_str}")

    if has_pets_str := extracted_info.get("has_pets"):
        if has_pets_str.strip():
            lead.has_pets_archived = has_pets_str.lower() == "true"
            updated = True

    if rented_before_str := extracted_info.get("rented_before"):
        if rented_before_str.strip():
            lead.rented_before_archived = rented_before_str.lower() == "true"
            updated = True

    if updated:
        db.commit()
        logging.info(f"✅ Updated Lead {lead.id} with extracted details")

    return updated
