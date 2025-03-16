import logging
from backend.fastapi.models.lead import Lead
from backend.fastapi.services.property_service import get_top_properties, format_property_list
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# this is to determine what fields are required for the current status to move forward
STATUS_REQUIRED_FIELDS = {
    "new": ["name", "property_interest"],
    "id_verification_requested": ["id_verified"],
    "id_verified": ["scheduled_showing_date"],
    # Add more if needed for later statuses
}

# 🔹 Missing Info Questions → Now Returns Structured Instructions
MISSING_INFO_QUESTIONS = {
    "name": "💡 The tenant has not provided their name yet. Politely ask for it in a friendly way. 😊",
    "property_interest": "💡 The tenant has not specified a property. Ask them which property they’re interested in. 🏠 If they seem unsure, suggest available options.",
    "id_verified": "💡 The tenant has not verified their ID yet. Ask them to send a photo of their ID to proceed. 📸",
}

# 🔹 Unique Handling for Showing Scheduled
def get_showing_scheduled_instructions(lead: Lead) -> str:
    return f"""
    The tenant has a showing scheduled for **{lead.scheduled_showing_date.strftime('%A, %B %d at %I:%M %p')}**. 

    💡 **Your Goal:**
    1️⃣ **Confirm their appointment** if they ask.  
    2️⃣ **Help them reschedule or cancel** if needed.  
    3️⃣ **Provide property details** if they have questions.  
    4️⃣ **Be concise and helpful.**  
    """

def get_missing_lead_info(db: Session, lead: Lead) -> str:
    """
    Dynamically checks what's missing for the current status and asks for it.
    """

    if lead.status == "showing_scheduled":
        return get_showing_scheduled_instructions(lead)

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
            
        elif lead.status == "id_verified":
            # ✅ Send the Calendly link instead of asking for a showing date
            # ✅ Fetch the property from the lead's property interest
            property_obj = lead.property_interest[0].property if lead.property_interest else None

            calendly_link = property_obj.calendly_link if property_obj and property_obj.calendly_link else "https://calendly.com/default-link"
            
            return (
                f"The tenant has successfully verified their ID. 🎉\n\n"
                "💡 **Next Step:** Provide them with the Calendly link to schedule a showing.\n"
                "1️⃣ Confirm that their ID verification is complete.\n"
                f"2️⃣ Send them the Calendly link: {calendly_link} 📅\n"
                "3️⃣ Offer to answer any questions they may have before their scheduled tour.\n\n"
                "Ensure the response is friendly and professional, guiding them through the process naturally."
            )
                    
        elif value in (None, "", False):
            logger.info(f"📌 Missing Info: {field} for Lead {lead.id}")
            return MISSING_INFO_QUESTIONS[field]

    # If nothing is missing, provide a helpful next-step message
    return STATUS_DEFAULT_MESSAGES.get(lead.status, "Thanks for your message! We'll get back to you shortly.")


STATUS_DEFAULT_MESSAGES = {
    "new": "Thanks for reaching out! Would you be interested in scheduling a viewing?",
    "id_verification_requested": "To move forward, please send a photo of your ID here. 📸 Once we receive it, we’ll schedule your showing.",
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
