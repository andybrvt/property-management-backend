import uuid
from sqlalchemy import Column, String, DateTime, UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.fastapi.dependencies.database import Base
from backend.fastapi.models.property import Property  # ✅ Import Property model

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)  # ✅ Store hashed passwords (never raw passwords)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    role = Column(String, default="owner")  # owner, tenant, admin
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    properties = relationship("Property", back_populates="owner", cascade="all, delete-orphan")  # ✅ Link to Property

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
