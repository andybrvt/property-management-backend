import logging
from backend.fastapi.models.lead import Lead

# ✅ Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_missing_lead_info(lead: Lead) -> str:
    """
    Determines the next follow-up question based on the lead's current status.
    """

    if lead.status == "new":
        if not lead.name or lead.name.lower() == "unknown":
            logger.info(f"📌 Missing Info: Name for Lead {lead.id}")
            return "Hey! What's your name? 😊"
        return "Thanks for reaching out! Would you be interested in scheduling a viewing?"

    if lead.status == "interested_in_showing":
        if not lead.email:
            logger.info(f"📌 Missing Info: Email for Lead {lead.id}")
            return "Sounds good! Can you share your best email? We’ll send you a secure link to verify your ID before scheduling."
        return "Perfect, we’ll be sending your ID verification link shortly!"

    if lead.status == "id_verification_requested":
        return "Just checking in—did you get a chance to upload your ID? Let me know if you need the link again."

    if lead.status == "id_verified":
        return "You're all set! Ready to book a showing? Here's my calendar link: **https://calendly.com/fake-link/30min**"

    if lead.status == "showing_scheduled":
        return "Looking forward to your showing! Let me know if any questions come up before then."

    if lead.status == "showing_completed":
        return "Hope you enjoyed the tour! Would you like the application link to move forward?"

    if lead.status == "application_sent":
        return "Just a reminder to complete your application when you get a chance!"

    if lead.status == "application_received":
        return "Thanks for applying! We're reviewing your info and will update you soon."

    if lead.status == "screening_in_progress":
        return "Your application is being screened—hang tight, we'll update you shortly."

    if lead.status == "approved":
        return "Congrats! You've been approved. We'll send over the lease shortly."

    if lead.status == "lease_sent":
        return "Let me know if you have any questions about the lease. We're here to help!"

    if lead.status == "lease_signed":
        return "Awesome! The next step is completing your payment. We'll send you the link shortly."

    if lead.status == "payment_pending":
        return "Reminder to complete your payment to secure the property!"

    if lead.status == "moved_in":
        return "Welcome home! Let us know if you need anything."

    if lead.status == "inactive":
        return "Hey, just checking in! Are you still interested in moving forward?"

    # Fallback if somehow no status matched
    return "Thanks for your message! We'll get back to you shortly."