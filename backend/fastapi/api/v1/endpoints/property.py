from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from backend.fastapi.dependencies.database import get_sync_db
from backend.fastapi.crud import property as property_crud
from backend.fastapi.schemas.property import PropertyCreate, PropertyResponse, PropertyUpdate
from backend.fastapi.services.property_service import attach_property_to_lead
from backend.fastapi.services import property_service  # ✅ make sure this import exists
from backend.fastapi.schemas.property import PropertyDropdownResponse
from backend.fastapi.models.property import Property
from fastapi.responses import JSONResponse
from backend.fastapi.crud.property import get_property_by_id, update_property_crud

router = APIRouter()

# ✅ Attach a property to a lead → POST /api/v1/properties/{property_id}/attach-to-lead/{lead_id}
@router.post("/{property_id}/attach-to-lead/{lead_id}", status_code=201)
def attach_property_to_lead(
    property_id: UUID,
    lead_id: UUID,
    db: Session = Depends(get_sync_db)
):
    """Attach a property to a lead as an interested property."""
    return property_service.attach_property_to_lead(
        db=db,
        lead_id=lead_id,
        property_id=property_id
    )

# ✅ Create a new property → POST /api/v1/properties/
@router.post("/", response_model=PropertyResponse, status_code=201)
def create_property(property_data: PropertyCreate, db: Session = Depends(get_sync_db)):
    """Create a new property"""
    return property_crud.create_property(db=db, property_data=property_data)

# ✅ Get a property by ID → GET /api/v1/properties/{property_id}
@router.get("/property/{property_id}", response_model=PropertyResponse)  # 🔹 Consistent path structure
def get_property(property_id: UUID, db: Session = Depends(get_sync_db)):
    """Retrieve a property by ID"""
    return property_crud.get_property_by_id(db, property_id=property_id)

# ✅ Get all properties → GET /api/v1/properties/list
@router.get("/list", response_model=List[PropertyResponse])  # 🔹 Avoids conflict with POST "/"
def get_properties(skip: int = 0, limit: int = 10, db: Session = Depends(get_sync_db)):
    """Retrieve all properties with pagination"""
    return property_crud.get_all_properties(db, skip=skip, limit=limit)

# ✅ Update a property → PUT /api/v1/properties/{property_id}
@router.put("/property/{property_id}", response_model=PropertyResponse)  # 🔹 Consistent with GET by ID
def update_property(property_id: UUID, property_data: PropertyUpdate, db: Session = Depends(get_sync_db)):
    """Update property details"""
    return property_crud.update_property_crud(db, property_id=property_id, property_data=property_data)


@router.get("/properties", response_model=List[PropertyDropdownResponse])
def get_all_properties(db: Session = Depends(get_sync_db)):
    """Fetch all properties for dropdown selection."""
    properties = db.query(Property).all()
    
    # ✅ Ensure ID is returned as a string
    return [PropertyDropdownResponse(id=str(p.id), address=p.address) for p in properties]

@router.put("/properties/{property_id}/calendly", response_model=PropertyResponse)
def update_property_calendly_link(
    property_id: UUID, 
    calendly_link: str, 
    db: Session = Depends(get_sync_db)
):
    """Update the Calendly link for a specific property."""

    # ✅ Ensure property exists before updating
    property_obj = get_property_by_id(db, property_id)

    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    # ✅ Pass `calendly_link` inside a PropertyUpdate instance
    property_update_data = PropertyUpdate(calendly_link=calendly_link)

    # ✅ Call update_property with correct data
    updated_property = update_property_crud(db, property_id, property_update_data)

    return updated_property

@router.delete("/delete-all", response_model=dict)
def delete_all_properties(db: Session = Depends(get_sync_db)):
    """Delete all properties from the database."""
    db.query(Property).delete()  # ✅ Delete all property records
    db.commit()  # ✅ Commit the transaction

    return {"message": "All properties have been deleted successfully."}