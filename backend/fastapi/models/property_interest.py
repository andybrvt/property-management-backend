from sqlalchemy import Column, String, DateTime, UUID, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from backend.fastapi.dependencies.database import Base


class PropertyInterest(Base):
    __tablename__ = "property_interest"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)  # Link to Lead
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)  # Link to Property

    status = Column(String, default="interested")  # 'interested', 'scheduled', 'not_interested', 'applied'
    scheduled_showing = Column(Boolean, default=False)  # Has the tenant scheduled a showing?
    application_submitted = Column(Boolean, default=False)  # Has the tenant submitted an application?
    
    created_at = Column(DateTime(), default=lambda: datetime.now(timezone.utc))

    # Relationships
    lead = relationship("Lead", back_populates="property_interest")
    property = relationship("Property", back_populates="interested_leads")

    def __repr__(self):
        return f"<PropertyInterest(lead_id={self.lead_id}, property_id={self.property_id}, status={self.status})>"
