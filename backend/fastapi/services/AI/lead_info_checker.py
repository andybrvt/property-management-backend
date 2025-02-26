import logging
from backend.fastapi.models.lead import Lead

# ✅ Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_missing_lead_info(lead: Lead) -> str:
    """
    Determines which piece of lead information is missing and returns the appropriate follow-up question.
    Prioritizes in order: Name > Move-in Date > Income > Pets > Rental History > Property Interest > Email.
    If all information is collected, sends a final confirmation and booking message.
    """

    if not lead.name or lead.name.lower() == "unknown":
        logger.info(f"📌 Missing Info: Name for Lead {lead.id}")
        return "By the way, what's your name? 😊"
    
    if not lead.move_in_date:
        logger.info(f"📌 Missing Info: Move-in Date for Lead {lead.id}")
        return "What’s your ideal move-in date? 🗓️"
    
    if lead.income is None:  # Allow 0 but not None
        logger.info(f"📌 Missing Info: Income for Lead {lead.id}")
        return "Can you share your monthly income range for qualification? 💰"
    
    if lead.has_pets is None:
        logger.info(f"📌 Missing Info: Pets for Lead {lead.id}")
        return "Do you have any pets? If so, what breed? 🐾"
    
    if lead.rented_before is None:
        logger.info(f"📌 Missing Info: Rental History for Lead {lead.id}")
        return "Have you rented before, or would this be your first time? 🏡"

    if not lead.property_interest:
        logger.info(f"📌 Missing Info: Property Interest for Lead {lead.id}")
        return "What type of property are you most interested in? A studio, 1-bedroom, or something else? 🏠"
    
    if not lead.email:
        logger.info(f"📌 Missing Info: Email for Lead {lead.id}")
        return "What’s the best email to reach you at? 📧"

    # ✅ If all required details are collected, send a follow-up message
    logger.info(f"✅ All required info collected for Lead {lead.id}")

    return (
        "Thanks for providing all your details! We've sent you an email with all the info you need. "
        "📅 You can now book a showing at your convenience here: **https://calendly.com/fake-link/30min**"
    )
