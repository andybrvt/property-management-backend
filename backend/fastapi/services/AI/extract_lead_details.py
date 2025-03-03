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
from backend.fastapi.services.ai.openai_client import call_openai
from backend.fastapi.utils.parsers import parse_extracted_lead_info
from backend.fastapi.services.lead.update_lead_mod import update_lead_with_extracted_info



def extract_lead_details_from_messages(db: Session, lead_id: int, session_id: str):
    """
    Key functions:

    - fetch session messages
    - craete ai prompt and call open ai 
    - parse json response 
    - update lead fields

    """
    
    # 🔹 1️⃣ Get all messages in this session
    session_messages = get_messages_by_session(db, session_id)

    # 🔹 2️⃣ Combine session messages for AI processing
    conversation_text = "\n".join([msg.content for msg in session_messages])

     # ✅ Use modular function to generate AI prompt
    extraction_prompt = get_lead_extraction_prompt(conversation_text)

    # ✅ LOGGING: Debugging full conversation
    logging.info(f"📝 Extracting details from conversation for Lead {lead_id}:\n{conversation_text}")

    # ✅ LOGGING: Log full AI prompt
    logging.info(f"📜 AI Extraction Prompt for Lead {lead_id}:\n{extraction_prompt}")

    extracted_data = call_openai(extraction_prompt, max_tokens=200)

    if not extracted_data:
        return
    
    # ✅ LOGGING: Debug extracted data
    logging.info(f"🔍 Extracted Data (Raw AI Response) for Lead {lead_id}: {extracted_data}")

    extracted_info = parse_extracted_lead_info(extracted_data)
    if not extracted_info:
        return

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return

    updated = update_lead_with_extracted_info(db, lead, extracted_info)  # Track if we make updates

    if updated:
        db.commit()  # Save updates to database
        logging.info(f"✅ Updated Lead {lead_id} with extracted details")
