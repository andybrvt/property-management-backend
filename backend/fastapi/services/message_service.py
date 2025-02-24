# services/message_service.py

from sqlalchemy.orm import Session
from backend.fastapi.crud.message import create_message, get_message, get_messages_for_lead, get_all_messages, update_message, delete_message
from typing import List, Dict
from uuid import UUID
from backend.fastapi.models.message import Message  # SQLAlchemy model
from backend.fastapi.schemas import MessageSchema  # Pydantic schema
from typing import Optional  
from fastapi import HTTPException



class MessageService:
    def __init__(self, db: Session):
        self.db = db

    def create_message(self, message_data: Dict) -> MessageSchema:
        """Create a new message"""
        db_message = create_message(self.db, message_data)  # Get SQLAlchemy model
        return MessageSchema.model_validate(db_message)  # Convert SQLAlchemy model to Pydantic model before returning

    '''
    async def create_message_async(self, message_data: Dict) -> MessageSchema:
        """Asynchronously create a new message"""
        db_message = await (self.db, message_data)  # Get SQLAlchemy model
        print('error here')
        return MessageSchema.from_orm(db_message)  # Convert SQLAlchemy model to Pydantic model

    '''
    
    def get_messages(self, skip: int, limit: int) -> List[MessageSchema]:
        """Retrieve messages with pagination"""
        db_messages = get_messages_for_lead(self.db, skip, limit)  # List of SQLAlchemy models
        return [MessageSchema.model_validate(message) for message in db_messages]  # Convert each to Pydantic model

    def get_all_messages(self, skip: int, limit: int) -> List[MessageSchema]:
        """Retrieve all messages with pagination"""
        db_messages = get_all_messages(self.db, skip, limit)  # List of SQLAlchemy models
        return [MessageSchema.model_validate(message) for message in db_messages]  # Convert each to Pydantic model
    
    def get_message(self, message_id: UUID) -> Optional[MessageSchema]:
        """Retrieve a single message by ID"""
        db_message = get_message(self.db, message_id)  # Fetch message from DB
        if db_message:
            return MessageSchema.model_validate(db_message)  # Convert to Pydantic schema
        return None  # Explicitly return None if message not found

    def update_message(self, message_id: UUID, message_data: Dict[str, any]) -> Optional[MessageSchema]:
        """Update an existing message"""
        db_message = update_message(self.db, message_id, message_data)  # Get updated SQLAlchemy model
        if db_message:
            return MessageSchema.model_validate(db_message)  # Convert to Pydantic schema
        return None  # Return None if the message was not found
    

    def delete_message(self, message_id: UUID) -> MessageSchema:
        """Delete a message by ID"""
        db_message = delete_message(self.db, message_id)  # Get SQLAlchemy model
        
        if db_message is None:  # ✅ If message isn't found, raise 404
            raise HTTPException(status_code=404, detail="Message not found")

        return MessageSchema.model_validate(db_message)  # ✅ Only validate if a message exists