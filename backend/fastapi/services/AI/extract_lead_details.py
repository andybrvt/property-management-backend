import openai
import os
import json
import re
from backend.fastapi.models.lead import Lead
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta
from backend.fastapi.crud.message import get_messages_by_session, get_latest_ai_message_for_lead
from backend.fastapi.services.ai.ai_prompts import get_lead_extraction_prompt
from backend.fastapi.services.ai.openai_client import call_openai_extraction
from backend.fastapi.utils.parsers import parse_extracted_lead_info
from backend.fastapi.services.lead.update_lead_mod import update_lead_with_extracted_info
from backend.fastapi.crud.lead import get_lead
from backend.fastapi.services.lead_service import update_lead_status_based_on_info
from backend.fastapi.services.property_service import handle_property_interest_from_extraction


def extract_lead_details_from_messages(db: Session, lead_id: int, session_id: str):
    """
    Extracts lead information from recent conversation history using AI,
    parses the data, and updates the lead record.

    Steps:
    1. Retrieve recent session messages.
    2. Combine messages into a single string to provide full context to the AI.
    3. Generate the extraction prompt, including current status.
    4. Call OpenAI to extract lead details.
    5. Clean and prepare the AI response for parsing.
    6. Parse the cleaned JSON and extract info.
    7. Update the lead with the extracted data.
    8. Update the lead's status based on newly filled information.
    9. Save changes to the database.
    """
    
    # Step 1: Fetch all messages from the current conversation session
    session_messages = get_messages_by_session(db, session_id)

    # Step 2: Combine the messages into one string to pass as conversation context
    conversation_text = "\n".join([msg.content for msg in session_messages])

    # Step 3: Retrieve the lead record
    lead = get_lead(db, lead_id)
    if not lead:
        return None
    
    # 🧠 NEW: Get the latest AI message sent to this lead
    latest_ai_message = get_latest_ai_message_for_lead(db, lead_id)

    if latest_ai_message:
        logging.info(f"📩 Latest AI message for context: {latest_ai_message.content}")
    else:
        logging.info("📩 No previous AI message found for this lead.")

    extraction_prompt = get_lead_extraction_prompt(
        conversation_text,
        current_status=lead.status,
        latest_ai_message=latest_ai_message.content if latest_ai_message else None
    )

    logging.info(f"📝 Extracting details from conversation for Lead {lead_id}:\n{conversation_text}")
    logging.info(f"📜 AI Extraction Prompt for Lead {lead_id}:\n{extraction_prompt}")

    # Step 5: Call the OpenAI extraction function
    extracted_data_raw = call_openai_extraction(extraction_prompt, max_tokens=200)
    if not extracted_data_raw:
        return

    # clean up ai response    
    logging.info(f"🔍 Extracted Data (Raw AI Response) for Lead {lead_id}: {extracted_data_raw}")
    cleaned_data = extracted_data_raw.strip()
    if cleaned_data.startswith("```json"):
        cleaned_data = cleaned_data.replace("```json", "").replace("```", "").strip()
    elif cleaned_data.startswith("```"):
        cleaned_data = cleaned_data.replace("```", "").replace("```", "").strip()
    extracted_info = parse_extracted_lead_info(cleaned_data)
    
    if not extracted_info or all(value is None for value in extracted_info.values()):
        logging.info(f"⚠️ No useful data extracted for Lead {lead_id}. Ignoring update.")
        return  # 🚨 Exit early if there are no real updates
    

    property_updated = False
    property_address = extracted_info.get("property_address_interest", "").strip()
    if property_address:
        property_updated = handle_property_interest_from_extraction(db, lead, property_address)

    # Step 8: Refresh the lead object to ensure it's the latest version
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return

    logging.info(f"🔍 Extracted Info for Lead {lead_id}: {extracted_info}")

    # Step 9: Update the lead with the extracted details
    lead_updated = update_lead_with_extracted_info(db, lead, extracted_info)  # Track if we make updates

    # Step 10: If any updates were made, update the status and commit the changes
    if lead_updated or property_updated:
        update_lead_status_based_on_info(db,lead)  # ✅ Run status updater here
        logging.info(f"✅ Updated Lead {lead_id} with extracted details")
