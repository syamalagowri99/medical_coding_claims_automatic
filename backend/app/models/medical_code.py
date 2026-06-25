from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class CodeSystem(str, enum.Enum):
    ICD_10 = "icd_10"
    CPT = "cpt"
    HCPCS = "hcpcs"


class CodeStatus(str, enum.Enum):
    SUGGESTED = "suggested"
    APPROVED = "approved"
    REJECTED = "rejected"


class MedicalCode(Base):
    __tablename__ = "medical_codes"

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, ForeignKey("extracted_entities.id"), nullable=False)
    code_system = Column(SQLEnum(CodeSystem), nullable=False)
    code = Column(String, nullable=False)
    description = Column(Text)
    confidence_score = Column(Float, default=0.0)
    status = Column(SQLEnum(CodeStatus), default=CodeStatus.SUGGESTED)
    approved_by = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    entity = relationship("ExtractedEntity", back_populates="medical_codes")
    approver = relationship("User", backref="approved_codes")
