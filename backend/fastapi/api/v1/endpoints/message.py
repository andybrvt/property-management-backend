from typing import List
from uuid import UUID
from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.fastapi.dependencies.database import get_sync_db
from backend.fastapi.schemas import MessageBase, MessageCreate, MessageSchema
from backend.fastapi.services.message_service import MessageService  # Import the service layer

router = APIRouter()

# Create a message endpoint
@router.post("/messages/", response_model=MessageSchema, status_code=status.HTTP_201_CREATED)
def create_message_endpoint(message_data: MessageCreate, db: Session = Depends(get_sync_db)):
    service = MessageService(db)  # Initialize the service with the DB session
    return service.create_message(message_data.model_dump())  # ✅ Use model_dump()

'''
# Async message creation
@router.post("/messages/async", response_model=MessageSchema, status_code=status.HTTP_201_CREATED)
async def create_message_async(message_data: MessageCreate, service: MessageService = Depends()):
    return await service.create_message_async(message_data)

'''

# Get all messages
@router.get("/messages/", response_model=List[MessageSchema], status_code=status.HTTP_200_OK)
def get_messages(skip: int = 0, limit: int = 30, db: Session = Depends(get_sync_db)):
    service = MessageService(db)  # Create the service using the injected session
    return service.get_all_messages(skip, limit)

# Get a single message
@router.get("/messages/{message_id}", response_model=MessageSchema, status_code=status.HTTP_200_OK)
def get_message_endpoint(message_id: UUID, db: Session = Depends(get_sync_db)):
    service = MessageService(db)  # Initialize the service with the DB session
    message = service.get_message(message_id)

    if message is None:  # Handle case where the message doesn't exist
        raise HTTPException(status_code=404, detail="Message not found")

    return message  # Return the found message

# Update message
@router.put("/messages/{message_id}", response_model=MessageSchema, status_code=status.HTTP_200_OK)
def update_message(message_id: UUID, message_data: MessageBase, db: Session = Depends(get_sync_db)):
    service = MessageService(db)
    return service.update_message(message_id, message_data.model_dump())

# Delete message
@router.delete("/messages/{message_id}", response_model=MessageSchema, status_code=status.HTTP_200_OK)
def delete_message(message_id: UUID, db: Session = Depends(get_sync_db)):
    service = MessageService(db)
    return service.delete_message(message_id)