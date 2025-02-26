import openai
import os
from backend.fastapi.crud.message import get_last_messages, save_ai_message, get_messages_by_session
from backend.fastapi.models.lead import Lead
from sqlalchemy.orm import Session
import logging
from backend.fastapi.services.AI.lead_info_checker import get_missing_lead_info
from backend.fastapi.services.AI.extract_lead_details import extract_lead_details_from_messages

# ✅ Set up logging
logging.basicConfig(level=logging.INFO)

# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def get_fallback_response(context_type: str) -> str:
    """Returns a fallback response based on conversation context."""
    fallbacks = {
        "opening": "Thanks for your message! We'll get back to you shortly.",
        "follow_up": "Thanks for your message! We'll get back to you shortly.",
        "escalation": "Thanks for your message! We'll get back to you shortly.",
        "general": "Thanks for your message! We'll get back to you shortly."
    }
    return fallbacks.get(context_type, fallbacks["general"])

def generate_ai_message(db: Session, lead_id: int, session_id: str, context: str, lead: Lead = None):
    """
    Generates a short, SMS-friendly AI response based on session context.
    - AI is given a knowledge base of FAQs and uses it for answering tenant questions.
    - AI answers tenant questions first, then asks for any missing details.
    - If no missing details, AI simply responds based on the provided context.
    """

    # 🔹 1️⃣ Extract details from conversation before determining missing info
    extract_lead_details_from_messages(db, lead_id, session_id)

    # 🔹 2️⃣ Get all messages in the session
    session_messages = get_messages_by_session(db, session_id)

    # ✅ LOGGING: Debugging session messages
    logging.info(f"📜 Session Messages for {session_id}: {session_messages}")

    # 🔹 3️⃣ Get the latest tenant message
    latest_tenant_message = next((msg.content for msg in reversed(session_messages) if msg.direction == "incoming"), None)

    # 🔹 4️⃣ Identify missing lead information
    missing_info_question = get_missing_lead_info(lead)

    # 🔹 5️⃣ Construct AI prompt with structured conversation context
    prompt = """
You are a professional, friendly leasing assistant responding to tenant inquiries via SMS.

### 📌 Knowledge Base (FAQ):
- **What is the rent?** The rent varies by property. Let me know which property you're interested in.
- **Are utilities included?** Utilities depend on the lease agreement. Some properties include them, while others don’t.
- **What is the pet policy?** We allow pets in some properties, but there may be restrictions. What kind of pet do you have?
- **What's the lease term?** Most leases are 12 months, but shorter terms may be available upon request.
- **Is parking included?** Parking availability depends on the property. Some have assigned spots, while others offer street parking.
- **How much is the security deposit?** Security deposits vary, but typically it's one month's rent.
- **What’s the move-in process?** Once approved, you'll sign the lease, pay the security deposit, and schedule a move-in date.
- **Do you accept Section 8?** Some properties do accept Section 8. Would you like me to check availability for you?

### 📌 Response Rules:
1️⃣ **Answer tenant questions first using the provided FAQ knowledge base.**  
2️⃣ **If relevant info isn’t found in the FAQ, respond as best as possible.**  
3️⃣ **If any lead details are missing, ask for only ONE missing piece of info.**  
4️⃣ **If all details are collected, confirm & provide a booking link.**  

### 🔍 Latest Tenant Messages:
"""

    if latest_tenant_message:
        prompt += f"\n📩 **Tenant Message:** {latest_tenant_message}"

    prompt += "\n\n### 🕰️ Previous Conversation History (For Context, Do Not Repeat):"

    # 🔹 6️⃣ Append missing info question (if applicable)
    if missing_info_question:
        prompt += f"\n\n💡 **Follow-up Question:** {missing_info_question}"
    else:
        # ✅ If all details are complete, send a well-structured closing message with a booking link
        return (
            f"Great! We’ve got everything we need. 🎉 Here’s a quick summary:\n\n"
            f"- **Move-in Date:** {lead.move_in_date.strftime('%Y-%m-%d') if lead.move_in_date else 'Not provided'}\n"
            f"- **Income:** ${lead.income if lead.income else 'Not provided'}\n"
            f"- **Pets:** {'Yes' if lead.has_pets else 'No'}\n"
            f"- **Rental History:** {'Yes' if lead.rented_before else 'No'}\n"
            f"- **Property Interest:** {lead.property_interest if lead.property_interest else 'Not provided'}\n\n"
            f"📅 Ready to book a showing? Schedule a time that works for you here: **[Book a Showing](https://calendly.com/fake-link/30min)**. "
            f"Let me know if you have any other questions! 😊"
        )

    # ✅ LOGGING: Final prompt before sending to GPT
    logging.info(f"📜 Final Prompt Sent to GPT:\n{prompt}")

    # 🔹 7️⃣ Send to GPT
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120  
        )
        ai_message = response.choices[0].message.content.strip()

        # 🔹 8️⃣ Save AI response to Messages table
        save_ai_message(db, lead_id, ai_message, session_id=session_id)

        return ai_message

    except Exception as e:
        logging.error(f"❌ OpenAI Error: {e}")
        return get_fallback_response(context)  # ✅ Uses context-based fallback response

