from sqlalchemy.orm import Session
from uuid import UUID
from backend.fastapi.models.lead import Lead
from backend.fastapi.schemas.lead import LeadCreate, LeadUpdate

# Create a new lead
def create_lead(db: Session, lead: LeadCreate):
    db_lead = Lead(**lead.dict())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

# Get a lead by ID
def get_lead(db: Session, lead_id: UUID):
    return db.query(Lead).filter(Lead.id == lead_id).first()

# Get all leads
def get_leads(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Lead).offset(skip).limit(limit).all()

# Update a lead
def update_lead(db: Session, lead_id: UUID, lead: LeadUpdate):
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if db_lead:
        for key, value in lead.dict(exclude_unset=True).items():
            setattr(db_lead, key, value)
        db.commit()
        db.refresh(db_lead)
    return db_lead

# Delete a lead
def delete_lead(db: Session, lead_id: UUID):
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if db_lead:
        db.delete(db_lead)
        db.commit()
    return db_lead
