from pydantic import BaseModel

class MassTextRequest(BaseModel):
    text: str
    address: str
