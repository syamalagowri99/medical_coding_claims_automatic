from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class EntityType(str, enum.Enum):
    DIAGNOSIS = "diagnosis"
    PROCEDURE = "procedure"
    MEDICATION = "medication"
    LAB_TEST = "lab_test"
    SYMPTOM = "symptom"
    OTHER = "other"


class ExtractedEntity(Base):
    __tablename__ = "extracted_entities"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    entity_type = Column(SQLEnum(EntityType), nullable=False)
    entity_text = Column(String, nullable=False)
    context = Column(Text)
    confidence_score = Column(Float, default=0.0)
    start_position = Column(Integer)
    end_position = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="extracted_entities")
    medical_codes = relationship("MedicalCode", back_populates="entity", cascade="all, delete-orphan")
