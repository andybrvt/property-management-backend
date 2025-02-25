import openai
import os

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

def generate_ai_message(context: str, lead=None, property_info=None):
    """
    Generate a short, SMS-friendly AI response based on the conversation context.
    If AI fails, a fallback response is used.
    """

    # Base system prompt (Keeps responses short, SMS-like, and human)
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

    # ✅ FIXED: Access attributes directly from the SQLAlchemy `Lead` object
    if lead:
        prompt += f"\n\nLead Info:\n"
        prompt += f"- Name: {lead.name if lead.name else 'Unknown'}\n"
        prompt += f"- Move-in Date: {lead.move_in_date if hasattr(lead, 'move_in_date') and lead.move_in_date else 'Not provided'}\n"
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
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"OpenAI Error: {e}")  # Log error for debugging
        return get_fallback_response(context)  # Use fallback response

