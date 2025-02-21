from sqlalchemy.orm import Session
from models.sms_message import SMSMessage
from schemas.sms_message import SMSMessageCreate

def create_sms_message(db: Session, message_data: dict):
    db_message = SMSMessage(**message_data)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_sms_messages(db: Session, lead_id: int):
    return db.query(SMSMessage).filter(SMSMessage.lead_id == lead_id).all()

def get_sms_message(db: Session, message_id: int):
    return db.query(SMSMessage).filter(SMSMessage.id == message_id).first()

def update_sms_status(db: Session, message_id: int, status: str):
    db_message = get_sms_message(db, message_id)
    if db_message:
        db_message.status = status
        db.commit()
        db.refresh(db_message)
    return db_message 