from fastapi import APIRouter, HTTPException
from schemas.user import UserCreate, UserResponse
from schemas.document import DocumentUpload, DocumentResponse
from typing import List

router = APIRouter(prefix="/api/v1")

@router.get("/")
async def root():
    return {"message": "CareerFlow AI API v1"}

@router.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    # This would normally interact with a database
    return UserResponse(
        id=1,
        email=user.email,
        full_name=user.full_name,
        created_at="2023-01-01T00:00:00Z"
    )

@router.post("/documents/upload/", response_model=DocumentResponse)
async def upload_document(document: DocumentUpload):
    # This would normally process the document
    return DocumentResponse(
        id=1,
        filename=document.filename,
        document_type=document.document_type,
        status="processed",
        processed_at="2023-01-01T00:00:00Z"
    )

@router.get("/health/")
async def health_check():
    return {"status": "healthy"}