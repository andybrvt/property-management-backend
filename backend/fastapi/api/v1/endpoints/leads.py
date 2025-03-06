from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from backend.fastapi.dependencies.database import get_sync_db
from backend.fastapi.crud import lead as lead_crud
from backend.fastapi.schemas.lead import LeadCreate, LeadSchema, LeadUpdate  # ✅ Fixed import
from typing import List
from backend.fastapi.utils.phone_utils import validate_phone
from backend.fastapi.services.lead_service import get_or_create_lead, update_lead_status_based_on_info
from backend.fastapi.services.message_service import store_message_log
from backend.fastapi.services.sms_service import send_sms, format_phone_number
from backend.fastapi.crud.lead import delete_lead
from backend.fastapi.services.ai_service import generate_ai_message
from pydantic import BaseModel
from backend.fastapi.services.ai.ai_prompts import get_lead_extraction_prompt
from backend.fastapi.services.ai.openai_client import call_openai_extraction
from backend.fastapi.services.ai.lead_info_checker import get_missing_lead_info
import json
import logging
from backend.fastapi.models.lead import Lead
from backend.fastapi.services.property_service import handle_property_interest_from_extraction

router = APIRouter()

# ✅ Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LeadTestExtractionRequest(BaseModel):
    conversation_text: str


from uuid import uuid4
from backend.fastapi.models.property_interest import PropertyInterest

# Test response 
@router.post("/test-missing-info")
def test_missing_info():
    """Test missing info checker for a fake lead."""

    # Create fake lead
    fake_lead = Lead(
        id=uuid4(),
        status="interested_in_showing",  # 🟡 Moved to 'interested_in_showing'
        name="Andy",
        email=None,                      # 🛑 Missing email
        property_interest=[],
    )

    # Add fake property interest to pass the earlier check
    fake_property_interest = PropertyInterest(
        id=uuid4(),
        lead_id=fake_lead.id,
        property_id=uuid4(),
        status="interested"
    )
    fake_lead.property_interest.append(fake_property_interest)

    question = get_missing_lead_info(fake_lead)

    return {
        "lead_status": fake_lead.status,
        "missing_info_question": question
    }

 
    

# Test extraction for lead
@router.post("/test-full-extraction")
def test_full_extraction(request: LeadTestExtractionRequest, db: Session = Depends(get_sync_db)):
    """Test extraction, lead update, property matching, and status update from sample conversation text."""
    conversation_text = request.conversation_text

    # ✅ Create a real lead in DB for testing (optional) or use an in-memory fake
    fake_lead = Lead(
        phone="5555555555",
        status="new",
        id_verified=True,
    )
    db.add(fake_lead)
    db.commit()
    db.refresh(fake_lead)

    # ✅ Generate the extraction prompt
    extraction_prompt = get_lead_extraction_prompt(conversation_text, current_status=fake_lead.status)

    logger.info(f"📜 Extraction Prompt:\n{extraction_prompt}")

    extracted_data_raw = call_openai_extraction(extraction_prompt, max_tokens=300)

    logger.info(f"🔍 Raw GPT Output:\n{extracted_data_raw}")

    # 🧹 Clean GPT markdown if needed
    cleaned_data = extracted_data_raw.strip()
    if cleaned_data.startswith("```json"):
        cleaned_data = cleaned_data.replace("```json", "").replace("```", "").strip()
    elif cleaned_data.startswith("```"):
        cleaned_data = cleaned_data.replace("```", "").replace("```", "").strip()

    try:
        extracted_data = json.loads(cleaned_data)
    except json.JSONDecodeError:
        logger.error(f"❌ JSON parsing failed. Cleaned output:\n{cleaned_data}")
        raise HTTPException(
            status_code=500,
            detail=f"❌ Failed to parse JSON from GPT response. Cleaned output: {cleaned_data}"
        )

    logger.info(f"✅ Parsed Extracted Data:\n{extracted_data}")

    # ✅ Apply extracted data to the lead
    # for key, value in extracted_data.items():
    #     if hasattr(fake_lead, key):
    #         setattr(fake_lead, key, value)

    # db.commit()

    # # ✅ Extract property address and attempt property match/attach
    # property_address = extracted_data.get("property_address_interest")
    # property_attached = handle_property_interest_from_extraction(db, fake_lead, property_address)

    # db.refresh(fake_lead)

    # # ✅ Run status updater
    # update_lead_status_based_on_info(fake_lead)
    # db.commit()

    # # ✅ Get attached properties to confirm
    # attached_properties = [
    #     {
    #         "property_id": pi.property_id,
    #         "status": pi.status
    #     }
    #     for pi in fake_lead.property_interest
    # ]

    # ✅ Return full test result
    # return {
    #     "prompt": extraction_prompt,
    #     "extracted_data": extracted_data,
    #     "final_lead_status": fake_lead.status,
    #     "property_address_interest": property_address,
    #     "property_attached": property_attached,
    #     "attached_properties": attached_properties,
    #     "lead_info": {
    #         "name": fake_lead.name,
    #         "email": fake_lead.email,
    #         "move_in_date": str(fake_lead.move_in_date) if fake_lead.move_in_date else None,
    #         "id_verified": fake_lead.id_verified,
    #     }
    # }

    return {
        "prompt": extraction_prompt,
        "extracted_data": extracted_data,
        "property_address_interest": extracted_data.get("property_address_interest"),
    }


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