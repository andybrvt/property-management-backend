from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
from backend.fastapi.models.property_interest import PropertyInterest
from backend.fastapi.models.property import Property
from typing import List
import logging
from backend.fastapi.models.lead import Lead



# ✅ Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def attach_property_to_lead(db: Session, lead_id: UUID, property_id: UUID):
    # Prevent duplicate property interest
    existing_interest = db.query(PropertyInterest).filter_by(
        lead_id=lead_id,
        property_id=property_id
    ).first()
    if existing_interest:
        raise HTTPException(
            status_code=400,
            detail=f"Lead {lead_id} is already interested in Property {property_id}."
        )

    property_interest = PropertyInterest(
        lead_id=lead_id,
        property_id=property_id,
        status="interested"
    )
    db.add(property_interest)
    db.commit()
    db.refresh(property_interest)
    return property_interest


def get_top_available_properties(db: Session, limit: int = 3) -> List[Property]:
    return db.query(Property).filter(
        Property.status == "available"
    ).limit(limit).all()


def get_property_by_address(db: Session, address: str) -> Property:
    return db.query(Property).filter(
        Property.address.ilike(f"%{address}%")
    ).first()


def handle_property_interest_from_extraction(
    db: Session, lead: Lead, property_address: str
):
    if not property_address:
        return False  # Nothing to do

    matched_property = get_property_by_address(db, property_address)
    
    if matched_property:
        # Check if already attached
        existing_interest = db.query(PropertyInterest).filter_by(
            lead_id=lead.id,
            property_id=matched_property.id
        ).first()
        
        if not existing_interest:
            attach_property_to_lead(
                db=db,
                lead_id=lead.id,
                property_id=matched_property.id
            )
            logging.info(f"🏠 Attached Property {matched_property.id} ({matched_property.address}) to Lead {lead.id}")
            return True  # Successfully attached
        else:
            logging.info(f"ℹ️ Lead {lead.id} already has interest in Property {matched_property.id}")
    else:
        logging.info(f"❌ No matching property found for address: '{property_address}'")
    
    return False  # No property attached