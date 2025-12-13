# This file is deprecated. All API routes have been consolidated into main.py
# to create a unified backend server.

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")

@router.get("/")
async def root():
    return {"message": "CareerFlow AI API v1 - Legacy Endpoint"}

@router.get("/health/")
async def health_check():
    return {"status": "healthy"}