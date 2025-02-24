from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from uuid import UUID
from backend.fastapi.utils.auth import hash_password  # ✅ Ensure passwords are hashed
from backend.fastapi.models.property import Property
from backend.fastapi.schemas.property import PropertyCreate, PropertyUpdate
from fastapi import HTTPException


def create_property(db: Session, property_data: PropertyCreate):
    """Create a new property in the database."""
    new_property = Property(**property_data.model_dump())
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    return new_property


def get_property_by_id(db: Session, property_id: UUID):
    """Retrieve a property by its ID."""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    return property_obj


def get_all_properties(db: Session, skip: int = 0, limit: int = 10):
    """Retrieve a paginated list of properties."""
    return db.query(Property).offset(skip).limit(limit).all()


def update_property(db: Session, property_id: UUID, property_data: PropertyUpdate):
    """Update an existing property."""
    property_obj = get_property_by_id(db, property_id)  # Fetch existing property
    update_data = property_data.model_dump(exclude_unset=True)  # Exclude fields not provided

    for key, value in update_data.items():
        setattr(property_obj, key, value)

    db.commit()
    db.refresh(property_obj)
    return property_obj


def delete_property(db: Session, property_id: UUID):
    """Delete a property by its ID."""
    property_obj = get_property_by_id(db, property_id)  # Fetch existing property
    db.delete(property_obj)
    db.commit()
    return {"message": "Property deleted successfully"}
