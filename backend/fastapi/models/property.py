import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.fastapi.dependencies.database import Base
from backend.fastapi.models.property_interest import PropertyInterest


class Property(Base):
    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    full_address = Column(String, nullable=True)    
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    num_bedrooms = Column(Integer, nullable=False)
    num_bathrooms = Column(Integer, nullable=False)
    sqft = Column(Integer, nullable=True)  # Optional square footage
    rent_price = Column(Integer, nullable=False)
    status = Column(String, default="available")  # available, occupied, under maintenance
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    calendly_link = Column(String, nullable=True)  # ✅ New field for scheduling link


    # Relationships
    owner = relationship("User", back_populates="properties")  # ✅ Link to User (property owner)
    interested_leads = relationship("PropertyInterest", back_populates="property", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<Property(id={self.id}, address={self.address}, status={self.status})>"
