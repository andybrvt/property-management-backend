from sqlalchemy import Column, Integer, String, Boolean, DateTime, UUID, ARRAY, JSON
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from backend.fastapi.dependencies.database import Base
from backend.fastapi.models.meeting import Meeting  
from backend.fastapi.models.employment_history import EmploymentHistory
from backend.fastapi.models.rental_history import RentalHistory
from backend.fastapi.models.property_interest import PropertyInterest


class Lead(Base):
    __tablename__ = 'leads'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zillow_application_id = Column(String, unique=True, nullable=True)  # Zillow application reference


    # Basic Info
    name = Column(String, index=True, nullable=True)  # Can be null initially
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True)  # Phone number from SMS


    # Lead Source
    source = Column(String, nullable=True)  # 'zillow', 'sms', 'web_form'
    status = Column(String, default="new")  # new, meeting_scheduled, 
    # Lead Status Progression
    # "new" → "meeting_scheduled" → "interested_after_showing" → "application_submitted" → "under_review" → "approved_pending_lease" → "lease_signed" → "moved_in" → ("unqualified" if lead fails)
    move_in_date = Column(DateTime, nullable=True)  # ✅ Added move-in date with time


    # Pets (old & new)
    pets_description = Column(String, nullable=True)  # New field for user-entered pet details

    # Screening
    credit_score = Column(Integer, nullable=True)
    background_check_status = Column(String, nullable=True)

    # Income & Financials
    total_income = Column(Integer, nullable=True)  # Total Monthly Income from Zillow or user input
    income_source_notes = Column(String, nullable=True)  # Notes on income (self-reported, paystub verified, etc.)

    # Showing & Engagement
    showing_scheduled = Column(Boolean, default=False)
    scheduled_showing_date = Column(DateTime, nullable=True)  # Actual date of the scheduled showing
    follow_up_status = Column(String, nullable=True)    


    # Ai tracking
    conversation_state = Column(String, default="initial")  # Track where we are in the conversation
    missing_info = Column(ARRAY(String), server_default="{}")

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_contact = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Verification
    id_verified = Column(Boolean, default=False)
    id_verification_date = Column(DateTime, nullable=True)

    # archived fields
    property_interest_archived = Column(String, nullable=True)  # Type of property interested in
    has_pets_archived = Column(Boolean, default=False)
    rented_before_archived = Column(Boolean, default=False)

    # property interest
    uncertain_interest = Column(Boolean, default=True)  # True if they seem unsure about a specific property
    interest_city = Column(String, nullable=True)  # Optional, helps narrow down property suggestions
    
    # Relationships
    messages = relationship("Message", back_populates="lead")
    employment_history = relationship("EmploymentHistory", back_populates="lead", cascade="all, delete-orphan")
    rental_history = relationship("RentalHistory", back_populates="lead", cascade="all, delete-orphan")
    property_interest = relationship("PropertyInterest", back_populates="lead", cascade="all, delete-orphan")
    

    def __repr__(self):
        return f"<Lead(id={self.id}, name={self.name}, phone={self.phone})>"
