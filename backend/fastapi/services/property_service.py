from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
from backend.fastapi.models.property_interest import PropertyInterest
from backend.fastapi.models.property import Property
from typing import List
import logging
from backend.fastapi.models.lead import Lead
from typing import Optional
from fuzzywuzzy import process  # ✅ For fuzzy matching



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
    """
    Finds a property by address. Uses:
    1. Exact match first
    2. Partial match (street, city, state)
    3. Fuzzy matching if needed
    """
    address = address.strip().lower()

    # Step 1️⃣: Try Exact Match First
    exact_match = db.query(Property).filter(
        Property.address.ilike(f"%{address}%")
    ).first()
    
    if exact_match:
        return exact_match  # ✅ Return immediately if exact match is found

        # Step 2️⃣: Try Substring Match
    potential_matches = db.query(Property).filter(
        Property.address.ilike(f"%{address}%")
    ).all()

    if potential_matches:
        return potential_matches[0]  # ✅ Return first partial match


    # Step 2️⃣: Try Partial Match (Street, City, State)
    properties = db.query(Property).all()  # ✅ Fetch all properties

    # ✅ Ignore properties with no full_address
    property_addresses = {
        prop.address.lower(): prop for prop in properties if prop.address
    }

    # Step 3️⃣: Use Fuzzy Matching to Rank Best Match
    if property_addresses:  # ✅ Ensure there's at least one valid address before running fuzzy matching
        best_match, confidence = process.extractOne(address, property_addresses.keys())

        if best_match and confidence > 80:  # ✅ Only return high-confidence matches
            return property_addresses[best_match]

    return None  # ❌ No match found


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
            lead.uncertain_interest = False  # ✅ Mark as certain now that we attached a valid property
            db.commit()
            db.refresh(lead)
            logging.info(f"🏠 Attached Property {matched_property.id} ({matched_property.address}) to Lead {lead.id}")
            return True  # Successfully attached
        else:
            logging.info(f"ℹ️ Lead {lead.id} already has interest in Property {matched_property.id}")
    else:
        logging.info(f"❌ No matching property found for address: '{property_address}'")
    
    return False  # No property attached


def get_top_properties(db: Session, city: Optional[str] = None, limit: int = 3) -> List[Property]:
    """
    Fetch top available properties, optionally filtered by city.
    """
    query = db.query(Property).filter(
        Property.status == "available"
    )
    if city:
        query = query.filter(Property.city.ilike(f"%{city}%"))
    
    top_properties = query.limit(limit).all()
    logging.info(f"🏡 Fetched {len(top_properties)} top properties{' in ' + city if city else ''}.")
    return top_properties


def format_property_list(properties: List[Property]) -> str:
    """
    Turn a list of Property objects into a clean, readable string.
    """
    if not properties:
        return "No available properties found at the moment."

    return "\n\n".join(
        f"🏠 {prop.address} — {prop.num_bedrooms}BR/{prop.num_bathrooms}BA, ${prop.rent_price}/mo"
        for prop in properties
    )

def get_calendly_link(db: Session, property_id: UUID) -> str:
    property = db.query(Property).get(property_id)
    if property and property.calendly_link:
        return property.calendly_link
    return "https://calendly.com/default"


def get_property_details(db: Session, lead: Lead) -> str:
    """
    Retrieves and formats property details for a lead's interested property.
    """
    if not lead:
        return ""

    property_interest = db.query(PropertyInterest).filter(PropertyInterest.lead_id == lead.id).first()
    if not property_interest:
        return ""

    property = db.query(Property).filter(Property.id == property_interest.property_id).first()
    if not property:
        return ""

    return f"""
🏡 **Property Details:**
- **Address:** {property.address}, {property.city}, {property.state} {property.zip_code}
- **Property Type:** {property.property_type or 'N/A'}
- **Bedrooms:** {property.num_bedrooms}
- **Bathrooms:** {property.num_bathrooms}
- **Square Feet:** {property.sqft or 'N/A'}
- **Rent Price:** ${property.rent_price}/month
- **Availability:** {property.status}
- **Move-in Date:** {property.available_date.strftime('%B %d, %Y') if property.available_date else 'N/A'}
- **Lease Duration:** {property.lease_duration or 'N/A'}
- **Security Deposit:** ${property.security_deposit or 'N/A'}
- **Calendly Link for Showings:** {property.calendly_link if property.calendly_link else 'N/A'}

🔹 **Financial Expectations:**
- **Landlord Pays:** {property.landlord_pays or 'N/A'}
- **Tenant Pays:** {property.tenant_pays or 'N/A'}
- **Renters Insurance Required:** {'Yes' if property.requires_renters_insurance else 'No'}

🔹 **Amenities & Features:**
- **Laundry:** {'Included' if property.has_laundry else 'Not included'}
- **Cooling:** {property.cooling_type or 'N/A'}
- **Appliances:** {property.appliances or 'N/A'}
- **Parking:** {property.parking_type or 'N/A'}
- **Outdoor Features:** {property.outdoor_features or 'N/A'}

🔹 **Pet Policy:**
- **Allows Pets:** {'Yes' if property.allows_pets else 'No'}
- **Pet Policy Notes:** {property.pet_policy_notes or 'N/A'}

📌 **How Showings & Next Steps Work:**
- Most people want to **see the property before applying**. That’s great!
- If you have questions about the property, ask me!
- If you need to reschedule, just let me know!
"""