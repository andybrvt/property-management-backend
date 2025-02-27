import logging
import openai
import os
from sqlalchemy.orm import Session
from backend.fastapi.crud.message import get_last_messages, save_ai_message, get_messages_by_session
from backend.fastapi.services.AI.lead_info_checker import get_missing_lead_info
from backend.fastapi.services.AI.extract_lead_details import extract_lead_details_from_messages
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
    Generates a short, SMS-friendly AI response based on session context.
    - AI prioritizes answering tenant questions using the FAQ knowledge base.
    - AI references past messages to avoid repetition.
    - AI asks for missing details if needed, guiding the conversation strategically.
    """

    # 🔹 Extract lead details from conversation
    extract_lead_details_from_messages(db, lead_id, session_id)

    # 🔹 Identify latest tenant messages
    latest_tenant_messages = get_messages_by_session(db, session_id)
    latest_tenant_messages = [msg.content for msg in latest_tenant_messages]

    # 🔹 Get last 10 messages (session history for context)
    session_messages = get_last_messages(db, lead_id, limit=10)
    # 🔹 Remove latest tenant messages from session history
    session_messages = [msg for msg in session_messages if msg["text"] not in latest_tenant_messages]  # ✅ Using dict key

    tenant_messages = [msg["text"] for msg in session_messages if msg["role"] == "tenant"]  # ✅ Using role-based filtering
    ai_messages = [msg["text"] for msg in session_messages if msg["role"] == "assistant"]  # ✅ Using role-based filtering

   
    # 🔹 Identify missing lead information
    missing_info_question = get_missing_lead_info(lead)

    # 🔹 Build AI prompt
    prompt = """
You are a professional, friendly leasing assistant responding to tenant inquiries via SMS.

### 📌 Knowledge Base (FAQ):
- **What is the rent?** Rent varies by property. Let me know which one you're interested in.
- **Are utilities included?** Some leases include utilities, while others do not.
- **What is the pet policy?** Some properties allow pets with restrictions. Do you have a pet?
- **What's the lease term?** Most leases are 12 months, but other options may be available.
- **Is parking included?** Parking varies by property—some have assigned spots, others street parking.
- **How much is the security deposit?** Typically one month’s rent, but varies by property.
- **What’s the move-in process?** Once approved, you'll sign the lease, pay the deposit, and schedule a move-in date.
- **Do you accept Section 8?** Some properties accept Section 8. Would you like me to check availability?

### 📌 Response Rules:
1️⃣ **Answer tenant questions first using the FAQ.**
2️⃣ **Avoid repeating previous AI responses.**
3️⃣ **Leverage the follow-up question to guide the conversation and gather missing details.**
4️⃣ **If all details are collected, confirm and provide next steps or answer any questions properly.**

### ⚠️ IMPORTANT GUIDELINES:
- 🚫 **DO NOT start messages with "Hi" or "Hello" unless the tenant greets first.**  
- 🔄 **Refer to past AI responses and tenant messages to avoid redundancy.**  
- ✅ **Keep responses tight, concise, and straight to the point.**  
- 🗣 **Speak in a natural, human-like tone. No overly formal or robotic phrasing.**  
- 🎯 **Focus on responding efficiently rather than adding unnecessary pleasantries.**  


### 🔍 Latest Tenant Messages:
"""
    
    if latest_tenant_messages:
        prompt += "\n".join(f"📩 {msg}" for msg in latest_tenant_messages)
    
    prompt += "\n\n### 🕰️ Previous Conversation History (For Context, Do Not Repeat):"
    
    if tenant_messages:
        prompt += "\n📩 **Past Tenant Messages:**\n" + "\n".join(f"- {msg}" for msg in tenant_messages[-5:])
    
    if ai_messages:
        prompt += "\n🤖 **Past AI Responses:**\n" + "\n".join(f"- {msg}" for msg in ai_messages[-5:])
    
    # 🔹 Append missing info question if applicable
    if missing_info_question:
        prompt += f"\n\n💡 **Follow-up Question:** {missing_info_question}"
    
    # ✅ LOGGING: Final prompt before sending to GPT
    logging.info(f"📜 Final Prompt Sent to GPT:\n{prompt}")
    
    # 🔹 Send prompt to GPT
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120
        )
        ai_message = response.choices[0].message.content.strip()

        # 🔹 Save AI response
        save_ai_message(db, lead_id, ai_message, session_id=session_id)
        return ai_message
    
    except Exception as e:
        logging.error(f"❌ OpenAI Error: {e}")
        return get_fallback_response(context)
