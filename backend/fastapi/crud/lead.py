from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
from backend.fastapi.models.lead import Lead
from backend.fastapi.schemas.lead import LeadCreate, LeadUpdate
import logging


# ✅ Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_lead_by_phone(db: Session, phone_number: str) -> Lead:
    """Retrieve a lead by phone number (low-level DB query)."""
    return db.query(Lead).filter(Lead.phone == phone_number).first()

    
def create_lead(db: Session, phone_number: str, **kwargs) -> Lead:
    """Creates a new lead in the database with optional extra fields."""
    try:
        lead_data = {"phone": phone_number, "status": "new"}
        lead_data.update(kwargs)  # ✅ Add extra fields dynamically

        db_lead = Lead(**lead_data)  # ✅ Uses only fields that exist in the Lead model
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)
        return db_lead  # ✅ Return the created lead

    except Exception as e:
        db.rollback()  # ✅ Rollback if anything goes wrong
        raise e  # ✅ Re-raise the error to be handled in `lead_service.py`


# Get a lead by ID
def get_lead(db: Session, lead_id: UUID):
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")  # ✅ Added 404 response
    return db_lead

# Get all leads
def get_leads(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Lead).offset(skip).limit(limit).all()

# Update a lead
def update_lead(db: Session, lead_id: UUID, lead: LeadUpdate):
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")  # ✅ Return 404 if lead is missing

    for key, value in lead.model_dump(exclude_unset=True).items():  # ✅ Fixed .dict() -> .model_dump()
        setattr(db_lead, key, value)

    db.commit()
    db.refresh(db_lead)
    return db_lead

# Delete a lead
def delete_lead(db: Session, lead_id: UUID):
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")  # ✅ Return 404 if lead is missing

    db.delete(db_lead)
    db.commit()
    return {"message": "Lead deleted successfully"}  # ✅ Return success message
