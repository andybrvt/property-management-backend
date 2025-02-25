import openai
import os
from backend.fastapi.crud.message import get_last_messages, save_ai_message
from backend.fastapi.models.lead import Lead
from sqlalchemy.orm import Session

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

def generate_ai_message(db: Session, lead_id: int, context: str, lead=None, property_info=None):
    """
    Generate a short, SMS-friendly AI response based on conversation context.
    - Fetches last messages for context.
    - Ensures AI doesn't repeat questions.
    - Saves AI response to the database.
    """

    # 🔹 1️⃣ Get conversation history for better context
    conversation_history = get_last_messages(db, lead_id, limit=3)  

    # 🔹 2️⃣ Build AI prompt with lead details and previous messages
    prompt = """
    You are a friendly, professional leasing assistant handling tenant inquiries via SMS.
    Your messages should be short (under 160 characters), human-like, and conversational.
    Avoid long paragraphs, unnecessary details, or formal language.
    Keep it natural, like a real leasing agent texting back.
    """

    if context == "opening":
        prompt += "\n\nA new lead has reached out. Craft a warm, engaging first text. Keep it casual and human."
    elif context == "follow_up":
        prompt += "\n\nA tenant has replied. Generate a natural follow-up question based on their response."
    elif context == "escalation":
        prompt += "\n\nThe AI needs help from a property manager. Generate a short escalation message summarizing key details."

    # 🔹 3️⃣ Append conversation history to prompt
    if conversation_history:
        prompt += "\n\nRecent conversation:\n"
        for msg in conversation_history:
            role = "Assistant" if msg["role"] == "assistant" else "Tenant"
            prompt += f"{role}: {msg['text']}\n"

    # 🔹 4️⃣ Include known lead details to avoid repeating questions
    if lead:
        prompt += f"\n\nLead Info:\n"
        prompt += f"- Name: {lead.name if lead.name else 'Unknown'}\n"
        
        # ✅ Fix move-in date formatting
        if lead.move_in_date:
            move_in_str = lead.move_in_date.strftime("%Y-%m-%d %I:%M %p")  # Format: YYYY-MM-DD HH:MM AM/PM
            prompt += f"- Move-in Date: {move_in_str}\n"
        else:
            prompt += "- Move-in Date: Not provided\n"
    
    prompt += f"- Income: {lead.income if lead.income else 'Not provided'}\n"
    if property_info:
        prompt += f"\n\nProperty Info:\n"
        prompt += f"- Address: {property_info.address if property_info.address else 'Unknown'}\n"
        prompt += f"- Rent: ${property_info.rent if property_info.rent else 'N/A'}/month\n"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )
        ai_message = response.choices[0].message.content.strip()

        # 🔹 5️⃣ Save AI response to Messages table
        save_ai_message(db, lead_id, ai_message)  

        return ai_message  # Return the AI-generated message

    except Exception as e:
        print(f"OpenAI Error: {e}")  # Log error for debugging
        return get_fallback_response(context)  # Use fallback response if AI fails

