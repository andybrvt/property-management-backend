import openai
import os
from backend.fastapi.crud.message import get_last_messages, save_ai_message
from backend.fastapi.models.lead import Lead
from sqlalchemy.orm import Session
import logging  # Add this at the top if not already imported

logging.basicConfig(level=logging.INFO)  # Ensure logging is enabled


# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY) 

def get_fallback_response(context_type: str) -> str:
    """Get appropriate fallback response based on the conversation context."""
    fallbacks = {
        "opening": "Hey there! Thanks for reaching out. When are you looking to move in?",
        "follow_up": "Got your message! Let me know if you have any questions about the rental.",
        "escalation": "We need a property manager to review this case. Someone will follow up shortly.",
        "general": "Thanks for your message! We'll get back to you shortly."
    }
    return fallbacks.get(context_type, fallbacks["general"])

def generate_ai_message(db: Session, lead_id: int, context: str, lead=None):
    """
    Generate a short, SMS-friendly AI response based on full session context.
    - AI first answers tenant's questions.
    - Then, AI asks a light follow-up question based on missing lead data.
    - Ensures AI does not repeat previous questions.
    """

    # 🔹 1️⃣ Get full session message history for better context
    conversation_history = get_last_messages(db, lead_id, limit=10)  

    # ✅ LOGGING: Print last 5 messages to debug
    logging.info(f"🗂️ Last 5 Messages for Lead {lead_id}: {conversation_history}")

    # 🔹 2️⃣ Structure conversation history for AI
    tenant_messages = []
    ai_messages = []
    for msg in conversation_history:
        if msg["role"] == "tenant":
            tenant_messages.append(msg["text"])
        else:
            ai_messages.append(msg["text"])

    # 🔹 3️⃣ Build AI prompt with structured context
    prompt = """
    You are a friendly, professional leasing assistant handling tenant inquiries via SMS.
    Your response **MUST**:
    - **First, answer all tenant questions directly** before asking anything.
    - **Then, ask one follow-up question** based on what information is missing.
    - **Avoid repeating** information already given.
    - Keep it short (under 160 characters) and natural.
    """

    if tenant_messages:
        prompt += "\n\n📩 **Tenant Messages:**\n" + "\n".join(f"- {msg}" for msg in tenant_messages)
    else:
        prompt += "\n\n📩 **No prior tenant messages.**"

    if ai_messages:
        prompt += "\n\n🤖 **Your Previous Responses:**\n" + "\n".join(f"- {msg}" for msg in ai_messages)

    # 🔹 4️⃣ Include known lead details
    prompt += "\n\n📌 **Lead Details:**\n"
    prompt += f"- Name: {lead.name if lead and lead.name else 'Unknown'}\n"
    prompt += f"- Move-in Date: {lead.move_in_date.strftime('%Y-%m-%d %I:%M %p') if lead and lead.move_in_date else 'Not provided'}\n"
    prompt += f"- Income: {lead.income if lead and lead.income else 'Not provided'}\n"
    prompt += f"- Pets: {'Yes' if lead and lead.has_pets else 'Not provided'}\n"

    # 🔹 5️⃣ Log the Final Prompt Before Sending to GPT
    logging.info(f"📜 Final Prompt Sent to GPT:\n{prompt}")

    # 🔹 6️⃣ Send the Prompt to GPT
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80  
        )
        ai_message = response.choices[0].message.content.strip()

        # 🔹 7️⃣ Save AI response to Messages table
        save_ai_message(db, lead_id, ai_message)  

        return ai_message  

    except Exception as e:
        logging.error(f"❌ OpenAI Error: {e}")  
        return get_fallback_response(context)  # ✅ Keep `context` for fallbacks
