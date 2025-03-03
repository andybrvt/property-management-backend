import logging
import openai
import os
from sqlalchemy.orm import Session
from backend.fastapi.services.message_service import save_ai_message, fetch_messages_by_session
from backend.fastapi.services.ai.lead_info_checker import get_missing_lead_info
from backend.fastapi.services.ai.extract_lead_details import extract_lead_details_from_messages
from backend.fastapi.services.message_service import get_last_messages
from backend.fastapi.services.ai.openai_client import call_openai
from backend.fastapi.services.ai.ai_prompts import build_ai_response_prompt
from backend.fastapi.services.message_service import get_conversation_context

# ✅ Load OpenAI API key

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

    # 🔹 Extract lead details from conversation
    extract_lead_details_from_messages(db, lead_id, session_id)

    
    latest_tenant_messages, tenant_messages, ai_messages = get_conversation_context(
        db, lead_id, session_id
    )
    
    # 🔹 Identify missing lead information
    missing_info_question = get_missing_lead_info(lead)

    # 🔹 Build AI prompt
    prompt = build_ai_response_prompt(
        latest_tenant_messages,
        tenant_messages,
        ai_messages,
        missing_info_question
    )

    # ✅ LOGGING: Final prompt before sending to GPT
    logging.info(f"📜 Final Prompt Sent to GPT:\n{prompt}")
    
    ai_message = call_openai(prompt, max_tokens=120)
    if not ai_message:
        return get_fallback_response(context)

    # ✅ Save the AI message after getting the response
    save_ai_message(db, lead_id, ai_message, session_id=session_id)

    return ai_message


