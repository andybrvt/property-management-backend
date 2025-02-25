import re

def validate_phone(phone_number: str) -> bool:
    """Validates if a phone number is correctly formatted (US format)."""
    pattern = re.compile(r"^\+1\d{10}$")  # Example: +12345678901
    return bool(pattern.match(phone_number))
