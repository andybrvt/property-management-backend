from sqlalchemy import Column, Integer, String, DateTime, UUID, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from backend.fastapi.dependencies.database import Base


class EmploymentHistory(Base):
    __tablename__ = "employment_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)  # Link to Lead

    job_title = Column(String, nullable=False)  # Example: "Software Engineer"
    company = Column(String, nullable=False)  # Example: "Google"
    employment_start = Column(DateTime, nullable=True)
    employment_end = Column(DateTime, nullable=True)
    employer_contact_name = Column(String, nullable=True)
    employer_contact_phone = Column(String, nullable=True)
    verification_status = Column(String, default="pending")  # 'pending', 'verified', 'failed'
    current_job = Column(Boolean, default=False)  # True if this is the current employer

    # Income Details
    monthly_income = Column(Integer, nullable=True)  # Monthly income for this specific job
    income_verified = Column(Boolean, default=False)  # True if income is verified with paystubs, tax docs, etc.

    created_at = Column(DateTime(), default=lambda: datetime.now(timezone.utc))

    # Relationships
    lead = relationship("Lead", back_populates="employment_history")

    def __repr__(self):
        return f"<EmploymentHistory(lead_id={self.lead_id}, company={self.company}, income={self.monthly_income})>"
