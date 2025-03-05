import openai
import os
import json
import re
from backend.fastapi.models.lead import Lead
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta
from backend.fastapi.crud.message import get_messages_by_session
from backend.fastapi.services.ai.ai_prompts import get_lead_extraction_prompt
from backend.fastapi.services.ai.openai_client import call_openai_extraction
from backend.fastapi.utils.parsers import parse_extracted_lead_info
from backend.fastapi.services.lead.update_lead_mod import update_lead_with_extracted_info
from backend.fastapi.crud.lead import get_lead
from backend.fastapi.services.lead_service import update_lead_status_based_on_info

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

    # Step 4: Generate the AI prompt to extract lead details
    extraction_prompt = get_lead_extraction_prompt(conversation_text, current_status=lead.status)

    # ✅ LOGGING: Debugging full conversation
    logging.info(f"📝 Extracting details from conversation for Lead {lead_id}:\n{conversation_text}")

    # ✅ LOGGING: Log full AI prompt
    logging.info(f"📜 AI Extraction Prompt for Lead {lead_id}:\n{extraction_prompt}")

    # Step 5: Call the OpenAI extraction function
    extracted_data_raw = call_openai_extraction(extraction_prompt, max_tokens=200)

    if not extracted_data_raw:
        return
    
    # ✅ LOGGING: Debug extracted data
    logging.info(f"🔍 Extracted Data (Raw AI Response) for Lead {lead_id}: {extracted_data_raw}")

    # Step 6: Clean up markdown wrapping if GPT added code block formatting
    cleaned_data = extracted_data_raw.strip()
    if cleaned_data.startswith("```json"):
        cleaned_data = cleaned_data.replace("```json", "").replace("```", "").strip()
    elif cleaned_data.startswith("```"):
        cleaned_data = cleaned_data.replace("```", "").replace("```", "").strip()

    
    # Step 7: Parse the cleaned JSON into a Python dictionary
    extracted_info = parse_extracted_lead_info(cleaned_data)
    if not extracted_info:
        return

    # Step 8: Refresh the lead object to ensure it's the latest version
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return


    # Step 9: Update the lead with the extracted details
    updated = update_lead_with_extracted_info(db, lead, extracted_info)  # Track if we make updates

    # Step 10: If any updates were made, update the status and commit the changes
    if updated:
        update_lead_status_based_on_info(lead)  # ✅ Run status updater here
        db.commit()  # Save updates to database
        logging.info(f"✅ Updated Lead {lead_id} with extracted details")
