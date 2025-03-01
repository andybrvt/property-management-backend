from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from backend.fastapi.dependencies.database import get_sync_db
from backend.fastapi.crud import lead as lead_crud
from backend.fastapi.schemas.lead import LeadCreate, LeadSchema, LeadUpdate  # ✅ Fixed import
from typing import List
from backend.fastapi.utils.phone_utils import validate_phone
from backend.fastapi.crud.lead import get_or_create_lead
from backend.fastapi.crud.message import store_message_log
from backend.fastapi.services.sms_service import send_sms, format_phone_number
from backend.fastapi.crud.lead import delete_lead
from backend.fastapi.services.ai_service import generate_ai_message

router = APIRouter()


@router.post("/start")
def start_lead_conversation(phone_number: str, db: Session = Depends(get_sync_db)):
    """Handles new lead creation. If lead exists, do nothing."""

    # Format and validate phone number
    formatted_number = format_phone_number(phone_number)
    if not formatted_number:
        raise HTTPException(status_code=400, detail="Invalid phone number. Must be a valid 10-digit US number.")

    # Check if lead already exists
    lead = get_or_create_lead(db, formatted_number, create_new=False)
    if lead:
        return {"message": "Lead already exists. No action taken.", "phone_number": formatted_number}

    # Lead does NOT exist, create and send first message
    lead = get_or_create_lead(db, formatted_number, create_new=True)

    # ✅ Generate AI-powered opening message
    #first_message = generate_ai_message("opening", lead)
    first_message = "Hey, thank you for reaching out. We are from xx and it seem like you were interested in one of our properites?"
    
    # Send SMS
    result = send_sms(formatted_number, first_message)

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error_message"])

    # Log the message in Messages table
    store_message_log(db, formatted_number, "outbound", first_message)

    return {"message": "AI conversation started", "phone_number": formatted_number}


@router.post("/", response_model=LeadSchema, status_code=201)
def create_lead(lead: LeadCreate, db: Session = Depends(get_sync_db)):
    """Create a new lead"""
    return lead_crud.create_lead(db=db, lead=lead)

@router.get("/", response_model=List[LeadSchema])
def get_all_leads(skip: int = 0, limit: int = 10, db: Session = Depends(get_sync_db)):
    """Get all leads with pagination"""
    return lead_crud.get_leads(db=db, skip=skip, limit=limit)


@router.get("/{lead_id}", response_model=LeadSchema)
def get_lead(lead_id: UUID, db: Session = Depends(get_sync_db)):
    """Get a lead by ID"""
    db_lead = lead_crud.get_lead(db, lead_id=lead_id)
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return db_lead

@router.put("/{lead_id}", response_model=LeadSchema)
def update_lead(lead_id: UUID, lead: LeadUpdate, db: Session = Depends(get_sync_db)):
    """Update a lead"""
    db_lead = lead_crud.update_lead(db, lead_id=lead_id, lead=lead)
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return db_lead


@router.delete("/delete/{lead_id}")
def delete_lead_by_id(lead_id: UUID, db: Session = Depends(get_sync_db)):
    """Deletes a lead by ID."""
    result = delete_lead(db, lead_id)
    if not result:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"message": "Lead deleted successfully", "lead_id": str(lead_id)}