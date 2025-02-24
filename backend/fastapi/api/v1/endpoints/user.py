from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from backend.fastapi.dependencies.database import get_sync_db
from backend.fastapi.crud import user as user_crud
from backend.fastapi.schemas.user import UserCreate, UserSchema, UserUpdate

router = APIRouter()

# ✅ Create a new user → POST /api/v1/users/
@router.post("/", response_model=UserSchema, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_sync_db)):
    """Create a new user"""
    return user_crud.create_user(db=db, user_data=user)

# ✅ Get a user by ID → GET /api/v1/users/{user_id}
@router.get("/user/{user_id}", response_model=UserSchema)  # 🔹 Changed path for clarity
def get_user(user_id: UUID, db: Session = Depends(get_sync_db)):
    """Retrieve a user by ID"""
    return user_crud.get_user_by_id(db, user_id=user_id)

# ✅ Get all users → GET /api/v1/users/list
@router.get("/list", response_model=List[UserSchema])  # 🔹 Avoids conflict with POST "/"
def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_sync_db)):
    """Retrieve all users with pagination"""
    return user_crud.get_users(db, skip=skip, limit=limit)

# ✅ Update a user → PUT /api/v1/users/{user_id}
@router.put("/user/{user_id}", response_model=UserSchema)  # 🔹 Made it consistent with GET by ID
def update_user(user_id: UUID, user: UserUpdate, db: Session = Depends(get_sync_db)):
    """Update user details"""
    return user_crud.update_user(db, user_id=user_id, user_data=user)
