from sqlalchemy import Column, Integer, String, DateTime, UUID, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from backend.fastapi.dependencies.database import Base


class RentalHistory(Base):
    __tablename__ = "rental_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)  # Link to Lead

    property_address = Column(String, nullable=False)  # Example: "123 Main St, NY"
    monthly_rent = Column(Integer, nullable=True)
    rental_start = Column(DateTime, nullable=True)
    rental_end = Column(DateTime, nullable=True)

    # Landlord Contact Info
    rental_manager_name = Column(String, nullable=True)
    rental_manager_phone = Column(String, nullable=True)
    rental_manager_email = Column(String, nullable=True)

    # Rental Verification (Trinary State Instead of Boolean)
    verification_status = Column(String, default="pending")  # 'pending', 'verified', 'failed'
    was_evicted = Column(String, default="unknown")  # 'yes' (confirmed), 'no' (confirmed false), 'unknown' (not answered)
    on_time_payment = Column(String, default="unknown")  # 'yes' (always on time), 'no' (late payments), 'unknown' (not answered)

    created_at = Column(DateTime(), default=lambda: datetime.now(timezone.utc))

    # Relationships
    lead = relationship("Lead", back_populates="rental_history")

    def __repr__(self):
        return f"<RentalHistory(lead_id={self.lead_id}, address={self.property_address}, was_evicted={self.was_evicted})>"
