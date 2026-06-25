from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.claim import ClaimStatus


class ClaimItemBase(BaseModel):
    code_id: Optional[int] = None
    service_date_start: Optional[datetime] = None
    service_date_end: Optional[datetime] = None
    procedure_code: Optional[str] = None
    diagnosis_code: Optional[str] = None
    amount: float = Field(default=0.0, ge=0.0)
    quantity: int = Field(default=1, ge=1)
    units: Optional[str] = None
    description: Optional[str] = None


class ClaimItemCreate(ClaimItemBase):
    claim_id: int


class ClaimItem(ClaimItemBase):
    id: int
    claim_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ClaimValidationBase(BaseModel):
    validation_type: str
    is_valid: bool = True
    error_message: Optional[str] = None
    severity: str = "error"


class ClaimValidation(ClaimValidationBase):
    id: int
    claim_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ClaimBase(BaseModel):
    patient_id: int
    insurance_provider: Optional[str] = None
    policy_number: Optional[str] = None
    rendering_provider_npi: Optional[str] = None
    place_of_service: Optional[str] = None
    total_amount: Optional[float] = Field(default=100.0, ge=0.0)


class ClaimCreate(ClaimBase):
    claim_number: str = Field(..., min_length=1, max_length=50)


class ClaimUpdate(BaseModel):
    status: Optional[ClaimStatus] = None
    insurance_provider: Optional[str] = None
    policy_number: Optional[str] = None
    rendering_provider_npi: Optional[str] = None
    place_of_service: Optional[str] = None
    notes: Optional[str] = None


class ClaimInDB(ClaimBase):
    id: int
    claim_number: str
    status: ClaimStatus
    total_amount: float
    submission_date: Optional[datetime]
    processing_date: Optional[datetime]
    rejection_reason: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Claim(ClaimInDB):
    claim_items: List[ClaimItem] = []
    validations: List[ClaimValidation] = []
