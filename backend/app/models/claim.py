from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class ClaimStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    DENIED = "denied"


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    claim_number = Column(String, unique=True, index=True, nullable=False)
    status = Column(SQLEnum(ClaimStatus), default=ClaimStatus.DRAFT)
    total_amount = Column(Float, default=0.0)
    insurance_provider = Column(String)
    policy_number = Column(String)
    rendering_provider_npi = Column(String, nullable=True)
    place_of_service = Column(String, nullable=True)  # e.g., "11" for office, "21" for inpatient
    submission_date = Column(DateTime(timezone=True))
    processing_date = Column(DateTime(timezone=True))
    rejection_reason = Column(Text)
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    patient = relationship("Patient", backref="claims")
    creator = relationship("User", backref="created_claims")
    claim_items = relationship("ClaimItem", back_populates="claim", cascade="all, delete-orphan")
    validations = relationship("ClaimValidation", back_populates="claim", cascade="all, delete-orphan")


class ClaimItem(Base):
    __tablename__ = "claim_items"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    code_id = Column(Integer, ForeignKey("medical_codes.id"))
    service_date_start = Column(DateTime(timezone=True))
    service_date_end = Column(DateTime(timezone=True))
    procedure_code = Column(String, nullable=True)  # CPT or HCPCS code
    diagnosis_code = Column(String, nullable=True)  # ICD-10 diagnosis code
    amount = Column(Float, default=0.0)
    quantity = Column(Integer, default=1)
    units = Column(String, nullable=True)  # e.g., "Minutes", "Units"
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    claim = relationship("Claim", back_populates="claim_items")
    medical_code = relationship("MedicalCode")


class ClaimValidation(Base):
    __tablename__ = "claim_validations"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    validation_type = Column(String, nullable=False)
    is_valid = Column(Boolean, default=True)
    error_message = Column(Text)
    severity = Column(String, default="error")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    claim = relationship("Claim", back_populates="validations")
