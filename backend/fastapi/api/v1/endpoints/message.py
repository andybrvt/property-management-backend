from typing import List
from uuid import UUID
from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.fastapi.dependencies.database import get_sync_db
from backend.fastapi.schemas import MessageBase, MessageCreate, MessageSchema
from backend.fastapi.services.message_service import (
    create_message, get_message, get_all_messages,
    update_message, delete_message
)

router = APIRouter()

# Create a message
@router.post("/messages/", response_model=MessageSchema, status_code=status.HTTP_201_CREATED)
def create_message_endpoint(message_data: MessageCreate, db: Session = Depends(get_sync_db)):
    return create_message(db, message_data.model_dump())  # ✅ Uses direct function call

# Get all messages
@router.get("/messages/", response_model=List[MessageSchema], status_code=status.HTTP_200_OK)
def get_messages(skip: int = 0, limit: int = 30, db: Session = Depends(get_sync_db)):
    return get_all_messages(db, skip, limit)  # ✅ Uses direct function call

# Get a single message
@router.get("/messages/{message_id}", response_model=MessageSchema, status_code=status.HTTP_200_OK)
def get_message_endpoint(message_id: UUID, db: Session = Depends(get_sync_db)):
    message = get_message(db, message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

# Update message
@router.put("/messages/{message_id}", response_model=MessageSchema, status_code=status.HTTP_200_OK)
def update_message_endpoint(message_id: UUID, message_data: MessageBase, db: Session = Depends(get_sync_db)):
    return update_message(db, message_id, message_data.model_dump())

# Delete message
@router.delete("/messages/{message_id}", response_model=MessageSchema, status_code=status.HTTP_200_OK)
def delete_message_endpoint(message_id: UUID, db: Session = Depends(get_sync_db)):
    return delete_message(db, message_id)
