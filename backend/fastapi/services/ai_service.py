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
    - AI first answers the **last 2 tenant messages.**
    - AI references broader conversation history **excluding the current session.**
    - AI asks **only one** missing detail question.
    """

    # 🔹 1️⃣ Get only the last 2 messages for immediate response focus
    last_two_messages = get_last_messages(db, lead_id, limit=2)  

    # ✅ LOGGING: Print last 2 messages to debug
    logging.info(f"🗂️ Last 2 Messages for Lead {lead_id}: {last_two_messages}")

    # 🔹 2️⃣ Fetch broader conversation history (excluding the last 2 messages)
    conversation_history = get_last_messages(db, lead_id, limit=10)  # Get a broader history
    conversation_history = [msg for msg in conversation_history if msg not in last_two_messages]  # Exclude last 2 messages

    # ✅ LOGGING: Print conversation history excluding last 2 messages
    logging.info(f"📜 Conversation History (Excluding Last 2) for Lead {lead_id}: {conversation_history}")

    # 🔹 3️⃣ Structure messages for AI
    recent_tenant_messages = [msg["text"] for msg in last_two_messages if msg["role"] == "tenant"]
    past_tenant_messages = [msg["text"] for msg in conversation_history if msg["role"] == "tenant"]
    past_ai_messages = [msg["text"] for msg in conversation_history if msg["role"] == "assistant"]

    # 🔹 4️⃣ Build AI prompt with structured context
    prompt = """
You are a friendly, professional leasing assistant handling tenant inquiries via SMS.

### 📌 Response Rules:
1️⃣ **Prioritize answering the last 2 tenant messages first.**  
2️⃣ **Reference past history (excluding these 2) to avoid repetition.**  
3️⃣ **Keep responses under 160 characters and natural.**  
4️⃣ **Ask only one follow-up question based on missing details.**  
5️⃣ **If all required info is provided, confirm and thank the tenant.**  

### 🔍 Latest 2 Messages (Tenant Priority):
"""

    if recent_tenant_messages:
        prompt += "\n".join(f"- {msg}" for msg in recent_tenant_messages)

    prompt += "\n\n### 🕰️ Previous Conversation History (For Context, Do Not Repeat):"
    
    if past_tenant_messages:
        prompt += "\n📩 **Past Tenant Messages:**\n" + "\n".join(f"- {msg}" for msg in past_tenant_messages)

    if past_ai_messages:
        prompt += "\n🤖 **Past AI Responses:**\n" + "\n".join(f"- {msg}" for msg in past_ai_messages)

    # 🔹 5️⃣ Include known lead details
    prompt += "\n\n📌 **Lead Details:**\n"
    prompt += f"- Name: {lead.name if lead and lead.name else 'Unknown'}\n"
    prompt += f"- Move-in Date: {lead.move_in_date.strftime('%Y-%m-%d %I:%M %p') if lead and lead.move_in_date else 'Not provided'}\n"
    prompt += f"- Income: {lead.income if lead and lead.income else 'Not provided'}\n"
    prompt += f"- Pets: {'Yes' if lead and lead.has_pets else 'Not provided'}\n"

    # 🔹 6️⃣ Log the Final Prompt Before Sending to GPT
    logging.info(f"📜 Final Prompt Sent to GPT:\n{prompt}")

    # 🔹 7️⃣ Send the Prompt to GPT
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80  
        )
        ai_message = response.choices[0].message.content.strip()

        # 🔹 8️⃣ Save AI response to Messages table
        save_ai_message(db, lead_id, ai_message)  

        return ai_message  

    except Exception as e:
        logging.error(f"❌ OpenAI Error: {e}")  
        return get_fallback_response(context)  # ✅ Use `context` for fallback


