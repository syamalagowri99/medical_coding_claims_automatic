from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.document import DocumentType, DocumentStatus


class DocumentBase(BaseModel):
    patient_id: int
    filename: str
    document_type: DocumentType = DocumentType.OTHER


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    document_type: Optional[DocumentType] = None
    status: Optional[DocumentStatus] = None


class DocumentInDB(DocumentBase):
    id: int
    file_type: Optional[str]
    file_size: Optional[int]
    status: DocumentStatus
    uploaded_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Document(DocumentInDB):
    content_text: Optional[str] = None


class DocumentUploadResponse(BaseModel):
    document_id: int
    filename: str
    status: str
    message: str
