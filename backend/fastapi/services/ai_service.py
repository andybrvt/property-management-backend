import logging
import openai
import os
from sqlalchemy.orm import Session
from backend.fastapi.services.message_service import save_ai_message, fetch_messages_by_session
from backend.fastapi.services.ai.lead_info_checker import get_missing_lead_info
from backend.fastapi.services.ai.extract_lead_details import extract_lead_details_from_messages
from backend.fastapi.services.message_service import get_last_messages
from backend.fastapi.services.ai.openai_client import call_openai_chat
from backend.fastapi.services.ai.ai_prompts import build_ai_message_history
from backend.fastapi.services.message_service import get_conversation_context

# ✅ Load OpenAI API key

# for better headspace as you build this out
# there are 3 main parts to this service
# 1️⃣ Extract + Update → 2️⃣ Check Status → 3️⃣ Send message
# Step 1 = Extraction.
# Step 2 = Conditions.
# Step 3 = Actions.




OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ✅ Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_fallback_response(context_type: str) -> str:
    """Returns a fallback response based on conversation context."""
    fallbacks = {
        "opening": "Thanks for your message! We'll get back to you shortly.",
        "follow_up": "Thanks for your message! We'll get back to you shortly.",
        "escalation": "Thanks for your message! We'll get back to you shortly.",
        "general": "Thanks for your message! We'll get back to you shortly."
    }
    return fallbacks.get(context_type, fallbacks["general"])

def generate_ai_message(db: Session, lead_id: int, session_id: str, context: str, lead=None):
    """
    Key segments of this function: 
    
    1. Extract lead details from conversation
    2. Retrive conversation history
    3. Identify missing lead information
    4. Build AI prompt
    5. Send to OpenAI + Save Response
    """

    # Step 1: Extract details + Update Info 
    extract_lead_details_from_messages(db, lead_id, session_id)


    # Step 2: Check Status 
    conversation_history = get_conversation_context(
        db, lead_id,
        limit=15  # ⬅️ Adjust this number as needed
    )

    # 🔹 Identify missing lead information
    missing_info_question = get_missing_lead_info(db,lead)


    # Step 3: Build AI prompt (send message out)
    messages = build_ai_message_history(
        conversation_history,
        missing_info_question
    )

    # ✅ LOGGING: Final messages before sending to GPT
    logging.info(f"📜 Final Messages Sent to GPT:\n{messages}")
    
    ai_message = call_openai_chat(messages, max_tokens=120)

    if not ai_message:
        return get_fallback_response(context)

    # ✅ Save the AI message after getting the response
    save_ai_message(db, lead_id, ai_message, session_id=session_id)

    return ai_message


