from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from backend.fastapi.dependencies.database import get_sync_db
from backend.fastapi.crud import property as property_crud
from backend.fastapi.schemas.property import PropertyCreate, PropertyResponse, PropertyUpdate

router = APIRouter()

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
    return property_crud.update_property(db, property_id=property_id, property_data=property_data)
