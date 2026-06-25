from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.entity import EntityType


class ExtractedEntityBase(BaseModel):
    entity_type: EntityType
    entity_text: str
    context: Optional[str] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)


class ExtractedEntityCreate(ExtractedEntityBase):
    document_id: int


class ExtractedEntityUpdate(BaseModel):
    entity_text: Optional[str] = None
    context: Optional[str] = None
    confidence_score: Optional[float] = None


class ExtractedEntityInDB(ExtractedEntityBase):
    id: int
    document_id: int
    start_position: Optional[int]
    end_position: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ExtractedEntity(ExtractedEntityInDB):
    medical_codes: List["MedicalCode"] = []


class MedicalCodeBase(BaseModel):
    code_system: str
    code: str
    description: Optional[str] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)


class MedicalCodeCreate(MedicalCodeBase):
    entity_id: int


class MedicalCodeUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    approved_by: Optional[int] = None


class MedicalCodeInDB(MedicalCodeBase):
    id: int
    entity_id: int
    status: str
    approved_by: Optional[int]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class MedicalCode(MedicalCodeInDB):
    pass
