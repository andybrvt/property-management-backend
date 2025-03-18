import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.fastapi.models.message import Message

logger = logging.getLogger(__name__)

async def wait_and_check_new_messages(db: Session, lead_id: str, cooldown_time: int = 5) -> bool:
    """Waits for cooldown and checks if newer messages arrived."""
    await asyncio.sleep(cooldown_time)

    latest_message = (
        db.query(Message)
        .filter(Message.lead_id == lead_id)
        .order_by(Message.sent_at.desc())
        .first()
    )

    if latest_message:
        last_message_time = latest_message.sent_at.replace(tzinfo=timezone.utc)
        current_time = datetime.now(timezone.utc)
        if (current_time - last_message_time).total_seconds() < cooldown_time:
            logger.info("🚨 Newer message detected during cooldown.")
            return True

    return False
