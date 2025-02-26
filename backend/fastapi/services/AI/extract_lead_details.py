import openai
import os
import json
import re
from backend.fastapi.models.lead import Lead
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta
from backend.fastapi.crud.message import get_messages_by_session

# ✅ Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def is_valid_email(email: str) -> bool:
    """Returns True if the email is valid and not empty, otherwise False."""
    if not email or email.strip() == "":  # Ignore empty strings
        return False
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(email_regex, email))

def extract_lead_details_from_messages(db: Session, lead_id: int, session_id: str):
    """
    Uses AI to analyze session messages and extract useful lead details.
    Updates the lead record with any extracted information.
    """

    # 🔹 1️⃣ Get all messages in this session
    session_messages = get_messages_by_session(db, session_id)

    # 🔹 2️⃣ Combine session messages for AI processing
    conversation_text = "\n".join([msg.content for msg in session_messages])

    # ✅ LOGGING: Debugging full conversation
    logging.info(f"📝 Extracting details from conversation for Lead {lead_id}:\n{conversation_text}")

    # 🔹 3️⃣ Get current date for better move-in date interpretation
    current_date = datetime.now().strftime("%Y-%m-%d")

    # 🔹 4️⃣ Define optimized AI prompt
    extraction_prompt = f"""
You are an AI assistant that extracts **subtle but important details** from a tenant's conversation.

### 📅 Today's Date: {current_date}

### 🎯 Extract the following details from the conversation:
- **name**: The tenant's full name (if mentioned).
- **move_in_date**: The exact expected move-in date (format: YYYY-MM-DD). If the tenant says "2 months from now," calculate the correct date from today.
- **income**: Monthly income as an integer (e.g., 4500).
- **has_pets**: Boolean (true/false) if the tenant has pets (e.g., "I have a dog" → true).
- **rented_before**: Boolean (true/false) if the tenant has rented before.
- **property_interest**: The type of property they are interested in (e.g., "Studio", "2-Bedroom").
- **email**: The tenant's email if provided.

### 📌 IMPORTANT INSTRUCTIONS:
- Detect **indirect or implied information** (e.g., "I have a dog" → `has_pets: true`).
- **Move-in Date:** If the tenant provides a relative date ("in 2 months"), convert it to a proper **YYYY-MM-DD** date.
- **Pets:** If the tenant asks about pets or mentions an animal, set **`has_pets: true`**.
- Ensure JSON output follows this exact format:
{{
    "name": "John Doe",
    "move_in_date": "2024-03-15",
    "income": 5000,
    "has_pets": true,
    "rented_before": false,
    "property_interest": "2-Bedroom",
    "email": "johndoe@email.com"
}}

### 📝 Tenant Conversation:
{conversation_text}

Return **only a valid JSON object**. Do NOT include explanations or extra text.
"""

    # ✅ LOGGING: Log full AI prompt
    logging.info(f"📜 AI Extraction Prompt for Lead {lead_id}:\n{extraction_prompt}")

    # 🔹 5️⃣ Send request to OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": extraction_prompt}],
            max_tokens=200  # Increased token limit for better data extraction
        )
        extracted_data = response.choices[0].message.content.strip()

        # ✅ LOGGING: Debug extracted data
        logging.info(f"🔍 Extracted Data (Raw AI Response) for Lead {lead_id}: {extracted_data}")

        # 🔹 6️⃣ Parse JSON response (handle errors safely)
        try:
            extracted_info = json.loads(extracted_data)
        except json.JSONDecodeError:
            logging.error("❌ Failed to parse AI response as JSON")
            return  # Exit early if AI response is malformed

        # 🔹 7️⃣ Update lead record with extracted details
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return

        updated = False  # Track if we make updates

        if "name" in extracted_info and not lead.name:
            lead.name = extracted_info["name"]
            updated = True
        if "move_in_date" in extracted_info and not lead.move_in_date:
            try:
                lead.move_in_date = datetime.strptime(extracted_info["move_in_date"], "%Y-%m-%d")
                updated = True
            except ValueError:
                logging.error(f"❌ Invalid date format received: {extracted_info['move_in_date']}")
        if "income" in extracted_info and (lead.income is None or lead.income == 0):  # ✅ Now allows updates if income is 0
            try:
                income_value = int(extracted_info["income"])
                lead.income = income_value
                updated = True
            except ValueError:
                logging.error(f"❌ Invalid income format received: {extracted_info['income']}")

        if "has_pets" in extracted_info and lead.has_pets is None:
            lead.has_pets = bool(extracted_info["has_pets"])
            updated = True
        if "rented_before" in extracted_info and lead.rented_before is None:
            lead.rented_before = bool(extracted_info["rented_before"])
            updated = True
        if "property_interest" in extracted_info and not lead.property_interest:
            lead.property_interest = extracted_info["property_interest"]
            updated = True
        if "email" in extracted_info:
            email_value = extracted_info["email"].strip()  # Remove extra spaces
            if is_valid_email(email_value):  
                lead.email = email_value
                updated = True
            else:
                logging.warning(f"⚠️ Skipping invalid or empty email: '{email_value}'")

        if updated:
            db.commit()  # Save updates to database
            logging.info(f"✅ Updated Lead {lead_id} with extracted details")

    except Exception as e:
        logging.error(f"❌ Error extracting lead details: {e}")
