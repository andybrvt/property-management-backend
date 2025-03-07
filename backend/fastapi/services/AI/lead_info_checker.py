import logging
from backend.fastapi.models.lead import Lead
from backend.fastapi.services.property_service import get_top_properties, format_property_list
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STATUS_REQUIRED_FIELDS = {
    "new": ["name", "property_interest"],
    "interested_in_showing": ["email"],
    "id_verification_requested": ["id_verified"],
    "id_verified": ["scheduled_showing_date"],
    # Add more if needed for later statuses
}

MISSING_INFO_QUESTIONS = {
    "name": "Hey! What's your name? 😊",
    "property_interest": "Which property are you interested in? 🏠",
    "email": "Sounds good! Can you share your best email? We’ll send you a secure link to verify your ID before scheduling.",
    "id_verified": "Just send you the email to verify your id before scheduling, let us know if you have any questions.",
    "scheduled_showing_date": "Great! When would you like to schedule your showing? 📅",
}

def get_missing_lead_info(db: Session, lead: Lead) -> str:
    """
    Dynamically checks what's missing for the current status and asks for it.
    """

    required_fields = STATUS_REQUIRED_FIELDS.get(lead.status, [])

    for field in required_fields:
        value = getattr(lead, field, None)
        if field == "property_interest":
            if lead.uncertain_interest:
                logger.info(f"🏡 Lead {lead.id} seems unsure. Suggesting properties.")
                top_properties = get_top_properties(db, city=lead.interest_city)
                property_list_text = format_property_list(top_properties)

                return f"""No worries if you're unsure! Here are a few available properties:\n\n{property_list_text}\n\nLet me know if any of these sound good! 🏡"""
            else:
                logger.info(f"📌 Missing Info: {field} for Lead {lead.id}")
                return MISSING_INFO_QUESTIONS[field]
        elif value in (None, "", False):
            logger.info(f"📌 Missing Info: {field} for Lead {lead.id}")
            return MISSING_INFO_QUESTIONS[field]

    # If nothing is missing, provide a helpful next-step message
    return STATUS_DEFAULT_MESSAGES.get(lead.status, "Thanks for your message! We'll get back to you shortly.")


STATUS_DEFAULT_MESSAGES = {
    "new": "Thanks for reaching out! Would you be interested in scheduling a viewing?",
    "interested_in_showing": "Perfect, we’ll be sending your ID verification link shortly!",
    "id_verification_requested": "We're waiting on your ID verification to continue.",
    "id_verified": "You're all set! Ready to book a showing? Here's my calendar link: **https://calendly.com/fake-link/30min**",
    "showing_scheduled": "Looking forward to your showing! Let me know if any questions come up before then.",
    "showing_completed": "Hope you enjoyed the tour! Would you like the application link to move forward?",
    "application_sent": "Just a reminder to complete your application when you get a chance!",
    "application_received": "Thanks for applying! We're reviewing your info and will update you soon.",
    "screening_in_progress": "Your application is being screened—hang tight, we'll update you shortly.",
    "approved": "Congrats! You've been approved. We'll send over the lease shortly.",
    "lease_sent": "Let me know if you have any questions about the lease. We're here to help!",
    "lease_signed": "Awesome! The next step is completing your payment. We'll send you the link shortly.",
    "payment_pending": "Reminder to complete your payment to secure the property!",
    "moved_in": "Welcome home! Let us know if you need anything.",
    "inactive": "Hey, just checking in! Are you still interested in moving forward?",
}
