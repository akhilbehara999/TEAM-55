from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentBase(BaseModel):
    filename: str
    document_type: str

class DocumentUpload(DocumentBase):
    content: str

class DocumentResponse(DocumentBase):
    id: int
    status: str
    processed_at: str

    class Config:
        from_attributes = True