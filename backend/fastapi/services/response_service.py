from backend.fastapi.models.lead import Lead
import openai
from typing import Dict, List
import json

async def generate_response(lead: Lead, message: str, context_data: Dict = None) -> str:
    """Generate AI response based on lead context and current message"""
    
    # Build context from lead information
    missing_fields = [
        field for field in ['name', 'income', 'has_pets', 'property_interest'] 
        if not getattr(lead, field)
    ]
    
    # Create system prompt based on conversation state
    system_prompt = f"""
    You are a helpful property management assistant. 
    Current lead information:
    - Name: {lead.name or 'Not provided'}
    - Income: {lead.income or 'Not provided'}
    - Has Pets: {lead.has_pets or 'Not provided'}
    - Property Interest: {lead.property_interest or 'Not provided'}
    
    Missing information: {', '.join(missing_fields)}
    
    Focus on collecting missing information naturally. Be friendly and conversational.
    If name is missing, ask for it first.
    Keep responses concise and suitable for SMS (under 160 characters when possible).
    """

    try:
        response = await openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=100  # Keep responses SMS-friendly
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        # Fallback to basic responses if AI fails
        if not lead.name:
            return "Hi! I'd love to help you find a property. Could you tell me your name?"
        elif not lead.property_interest:
            return f"Thanks {lead.name}! What type of property are you interested in?"
        elif not lead.income:
            return "To help find the right property, could you share your monthly income?"
        elif lead.has_pets is None:
            return "Do you have any pets that would be living with you?"
        else:
            return "Thank you for providing that information. How else can I help you today?" 