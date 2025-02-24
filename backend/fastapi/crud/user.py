from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
from backend.fastapi.models.user import User
from backend.fastapi.schemas.user import UserCreate, UserUpdate
from backend.fastapi.utils.auth import hash_password  # ✅ Ensure passwords are hashed

# ✅ Create a new user
def create_user(db: Session, user_data: UserCreate):
    """Create a new user and store hashed password."""
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user_data.password)  # ✅ Hash password before storing
    db_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        role=user_data.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ✅ Get a user by ID
def get_user_by_id(db: Session, user_id: UUID):
    """Retrieve a user by their unique ID."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# ✅ Get a user by email (for authentication)
def get_user_by_email(db: Session, email: str):
    """Retrieve a user by their email (useful for login)."""
    return db.query(User).filter(User.email == email).first()

# ✅ Get all users with pagination
def get_users(db: Session, skip: int = 0, limit: int = 10):
    """Retrieve a list of users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()

# ✅ Update an existing user
def update_user(db: Session, user_id: UUID, user_data: UserUpdate):
    """Update user details (supports partial updates)."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)  # ✅ Only update provided fields
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))  # ✅ Re-hash new password

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user

# ✅ Delete a user
def delete_user(db: Session, user_id: UUID):
    """Delete a user by ID."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
