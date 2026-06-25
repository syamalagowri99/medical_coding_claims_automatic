from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.schemas.claim import ClaimCreate, ClaimUpdate, Claim, ClaimItemCreate
from app.services.claim_service import (
    create_claim, add_claim_item, validate_claim, submit_claim,
    get_claim, get_claims_by_patient, update_claim,
    approve_code, reject_code, approve_claim, reject_claim
)
from app.core.deps import get_current_active_user
from app.models.user import User as UserModel

router = APIRouter()


@router.post("/", response_model=Claim, status_code=status.HTTP_201_CREATED)
async def create_claim_endpoint(
    claim: ClaimCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new claim."""
    try:
        return create_claim(db, claim, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=list[Claim])
async def list_claims(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all claims with pagination."""
    from app.models.claim import Claim as ClaimModel
    claims = db.query(ClaimModel).offset(skip).limit(limit).all()
    return claims


@router.get("/patient/{patient_id}", response_model=list[Claim])
async def get_patient_claims(
    patient_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all claims for a patient."""
    return get_claims_by_patient(db, patient_id)


@router.get("/{claim_id}", response_model=Claim)
async def get_claim_by_id(
    claim_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get claim by ID."""
    claim = get_claim(db, claim_id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    return claim


@router.put("/{claim_id}", response_model=Claim)
async def update_claim_endpoint(
    claim_id: int,
    claim_update: ClaimUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update claim information."""
    try:
        return update_claim(db, claim_id, claim_update)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{claim_id}/items", response_model=Claim)
async def add_claim_item_endpoint(
    claim_item: ClaimItemCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add an item to a claim."""
    try:
        add_claim_item(db, claim_item)
        return get_claim(db, claim_item.claim_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{claim_id}/validate", response_model=Claim)
async def validate_claim_endpoint(
    claim_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Validate a claim."""
    try:
        return validate_claim(db, claim_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{claim_id}/submit", response_model=Claim)
async def submit_claim_endpoint(
    claim_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit a claim for processing."""
    try:
        return submit_claim(db, claim_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/codes/{code_id}/approve", status_code=status.HTTP_200_OK)
async def approve_code_endpoint(
    code_id: int,
    notes: str = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Approve a suggested medical code."""
    try:
        approve_code(db, code_id, current_user.id, notes)
        return {"message": "Code approved successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/codes/{code_id}/reject", status_code=status.HTTP_200_OK)
async def reject_code_endpoint(
    code_id: int,
    notes: str = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Reject a suggested medical code."""
    try:
        reject_code(db, code_id, current_user.id, notes)
        return {"message": "Code rejected successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{claim_id}/approve", response_model=Claim, status_code=status.HTTP_200_OK)
async def approve_claim_endpoint(
    claim_id: int,
    notes: str = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Approve a submitted claim."""
    try:
        return approve_claim(db, claim_id, current_user.id, notes)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{claim_id}/reject", response_model=Claim, status_code=status.HTTP_200_OK)
async def reject_claim_endpoint(
    claim_id: int,
    rejection_reason: str,
    notes: str = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Reject a submitted claim."""
    try:
        return reject_claim(db, claim_id, current_user.id, rejection_reason, notes)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
