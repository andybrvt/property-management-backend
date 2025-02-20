from fastapi import FastAPI
from backend.fastapi.api.v1.endpoints import base, doc, message, sms

def setup_routers(app: FastAPI):
    app.include_router(base.router, prefix="", tags=["main"])
    app.include_router(doc.router, prefix="", tags=["doc"])
    app.include_router(message.router, prefix="/api/v1", tags=["message"])
    app.include_router(sms.router, prefix="/api/v1", tags=["sms"])
