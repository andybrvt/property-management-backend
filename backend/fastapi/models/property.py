import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, UUID, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.fastapi.dependencies.database import Base
from backend.fastapi.models.property_interest import PropertyInterest


class Property(Base):
    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Address Info
    full_address = Column(String, nullable=True)    
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)

    # Property Info
    property_type = Column(String, nullable=True)  # ✅ "Townhouse", "Apartment", "Single Family Home"
    num_bedrooms = Column(Integer, nullable=False)
    num_bathrooms = Column(Integer, nullable=False)
    sqft = Column(Integer, nullable=True)  # Optional square footage
    rent_price = Column(Integer, nullable=False)
    status = Column(String, default="available")  # available, occupied, under maintenance
    


    # 🔹 Lease & Availability
    lease_duration = Column(String, nullable=True)  # ✅ "12 months", "6 months", etc.
    available_date = Column(DateTime, nullable=True)  # ✅ Move-in availability date

    # 🔹 Financial Terms
    landlord_pays = Column(String, nullable=True)  # ✅ What the landlord covers (e.g., "HOA, water, snow removal")
    tenant_pays = Column(String, nullable=True)  # ✅ What the tenant pays (e.g., "utilities")
    security_deposit = Column(Integer, nullable=True)  # ✅ Security deposit amount
    
    requires_renters_insurance = Column(Boolean, default=False)  # ✅ Does the landlord require renters insurance?

    # 🔹 Amenities & Features
    has_laundry = Column(Boolean, default=False)  # ✅ Washer/dryer included?
    cooling_type = Column(String, nullable=True)  # ✅ "Central A/C", "Window Unit", etc.
    appliances = Column(String, nullable=True)  # ✅ "Dishwasher, Microwave, Oven, Fridge"
    parking_type = Column(String, nullable=True)  # ✅ "Detached garage", "Street parking"
    outdoor_features = Column(String, nullable=True)  # ✅ "Balcony, Patio, Backyard"

    # 🔹 Pet Policy
    allows_pets = Column(Boolean, default=False)  # ✅ Does the property allow pets?
    pet_policy_notes = Column(String, nullable=True)  # ✅ Additional pet rules (e.g., "Pet policy is non-negotiable")




    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    calendly_link = Column(String, nullable=True)  # ✅ New field for scheduling link


    # Relationships
    owner = relationship("User", back_populates="properties")  # ✅ Link to User (property owner)
    interested_leads = relationship("PropertyInterest", back_populates="property", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<Property(id={self.id}, address={self.address}, status={self.status})>"
