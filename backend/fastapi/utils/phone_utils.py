import re
from backend.fastapi.services.ai.openai_client import call_openai_extraction


def validate_phone(phone_number: str) -> bool:
    """Validates if a phone number is correctly formatted (US format)."""
    pattern = re.compile(r"^\+1\d{10}$")  # Example: +12345678901
    return bool(pattern.match(phone_number))


# ✅ GPT-powered extraction
def extract_phone_numbers_gpt(text: str) -> list:
    prompt = f"""
    Extract all valid US phone numbers from the following text. 
    Only return the phone numbers as a comma-separated list (no other text):

    {text}
    """
    raw_response = call_openai_extraction(prompt, max_tokens=150)
    numbers = [num.strip() for num in raw_response.split(',') if num.strip()]
    return numbers