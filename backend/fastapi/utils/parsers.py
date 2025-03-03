import json
import logging

def parse_extracted_lead_info(extracted_data: str) -> dict:
    """
    Safely parse extracted lead info from AI response JSON.
    Returns an empty dict if parsing fails.
    """
    try:
        return json.loads(extracted_data)
    except json.JSONDecodeError:
        logging.error("❌ Failed to parse AI response as JSON")
        return {}
