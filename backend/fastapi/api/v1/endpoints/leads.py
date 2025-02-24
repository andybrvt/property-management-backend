from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from backend.fastapi.dependencies.database import get_db
from backend.fastapi.crud import lead as lead_crud
from backend.fastapi.schemas.lead import LeadCreate, Lead, LeadUpdate

router = APIRouter()

@router.post("/", response_model=Lead)
def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    """Create a new lead"""
    return lead_crud.create_lead(db=db, lead=lead)

@router.get("/{lead_id}", response_model=Lead)
def get_lead(lead_id: UUID, db: Session = Depends(get_db)):
    """Get a lead by ID"""
    db_lead = lead_crud.get_lead(db, lead_id=lead_id)
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return db_lead

@router.put("/{lead_id}", response_model=Lead)
def update_lead(lead_id: UUID, lead: LeadUpdate, db: Session = Depends(get_db)):
    """Update a lead"""
    db_lead = lead_crud.update_lead(db, lead_id=lead_id, lead=lead)
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return db_lead 