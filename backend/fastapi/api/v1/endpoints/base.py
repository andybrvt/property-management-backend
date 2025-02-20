import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Request


router = APIRouter()

@router.get("/")
async def onboard_message(request: Request):
    # If you have custom authentication checks, you can bypass here.
    if 'authenticated' not in request.session:
        return JSONResponse(content={"message": "You've been onboarded!"}, status_code=200)
    return {"message": "You've been onboarded!"}