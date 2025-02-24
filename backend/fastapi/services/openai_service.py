import openai
from typing import Optional, Dict, List
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define default system prompts for different contexts
SYSTEM_PROMPTS = {
    "property_management": """You are a helpful property management assistant. 
    Keep responses friendly but professional and under 160 characters for SMS.
    Focus on collecting essential information and providing clear, concise responses.""",
    
    "general": """You are a helpful professional assistant.
    Keep responses friendly, professional, and concise.
    Focus on providing clear and helpful information.""",
    
    "customer_service": """You are a customer service professional.
    Keep responses friendly, empathetic, and solution-oriented.
    Maintain a professional tone while being helpful."""
}

async def generate_response(
    message: str,
    context_type: str = "property_management",
    custom_system_prompt: Optional[str] = None,
    context_data: Optional[Dict[str, str]] = None,
    max_tokens: int = 100,
    temperature: float = 0.7,
    message_history: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Generate AI response based on input message and context.
    
    Args:
        message: The user's input message
        context_type: Type of conversation context ("property_management", "general", "customer_service")
        custom_system_prompt: Optional custom system prompt to override defaults
        context_data: Dictionary of additional context information
        max_tokens: Maximum tokens in response
        temperature: Response creativity (0.0 to 1.0)
        message_history: Optional list of previous messages for context
    
    Returns:
        str: Generated response
    """
    # Select or create system prompt
    system_prompt = custom_system_prompt or SYSTEM_PROMPTS.get(
        context_type, 
        SYSTEM_PROMPTS["general"]
    )

    # Build context string from context_data if provided
    context = ""
    if context_data:
        context = "Context Information:\n" + "\n".join(
            f"{k}: {v or 'Unknown'}" 
            for k, v in context_data.items()
        ) + "\n"
    context += f"User message: {message}"

    # Prepare messages for the API call
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add message history if provided
    if message_history:
        messages.extend(message_history)
    
    # Add current context and message
    messages.append({"role": "user", "content": context})

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Log the error here if needed
        return get_fallback_response(context_type)

def get_fallback_response(context_type: str) -> str:
    """Get appropriate fallback response based on context"""
    fallbacks = {
        "property_management": "Thanks for your message! We'll get back to you shortly. For immediate assistance, please call our office.",
        "customer_service": "Thank you for reaching out. We're experiencing technical difficulties. Please try again shortly or contact our support team.",
        "general": "Thank you for your message. We'll respond as soon as possible."
    }
    return fallbacks.get(context_type, fallbacks["general"]) 