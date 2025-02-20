from pydantic import BaseModel, Field
from pydantic.types import constr
import re

class SMSRequest(BaseModel):
    to_number: str = Field(
        ...,
        pattern=r"^\+[1-9]\d{1,14}$",
        description="Phone number in E.164 format (e.g., +14155552671)"
    )
    message_text: str = Field(
        ...,
        min_length=1,
        max_length=1600,
        description="Message text to send"
    )

class SMSResponse(BaseModel):
    status: str
    message_sid: str | None = None
    error_message: str | None = None 