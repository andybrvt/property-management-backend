from sqlalchemy.orm import Session
from models.lead import Lead
from schemas.lead import LeadCreate, LeadUpdate

def create_lead(db: Session, lead_data: dict):
    db_lead = Lead(**lead_data)
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

def get_lead(db: Session, lead_id: int):
    return db.query(Lead).filter(Lead.id == lead_id).first()

def get_lead_by_phone(db: Session, phone: str):
    return db.query(Lead).filter(Lead.phone == phone).first()

def update_lead(db: Session, lead_id: int, lead: LeadUpdate):
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if db_lead:
        for key, value in lead.dict(exclude_unset=True).items():
            setattr(db_lead, key, value)
        db.commit()
        db.refresh(db_lead)
    return db_lead 