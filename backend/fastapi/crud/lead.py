from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
from backend.fastapi.models.lead import Lead
from backend.fastapi.schemas.lead import LeadCreate, LeadUpdate

# Create a new lead
def create_lead(db: Session, lead: LeadCreate):
    db_lead = Lead(**lead.model_dump())  # ✅ Fixed .dict() -> .model_dump()
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

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
