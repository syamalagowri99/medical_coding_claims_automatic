#!/usr/bin/env python
"""Create comprehensive sample claims with complete clinical and billing data."""
import sys
from datetime import datetime, timedelta

try:
    # Import the main app first to ensure all models are registered
    import app.main
    from app.db.database import SessionLocal
    from app.models.user import User
    from app.models.patient import Patient
    from app.models.claim import Claim, ClaimStatus, ClaimItem
    from app.core.security import get_password_hash
    
    db = SessionLocal()
    
    # Get or create test user
    test_user = db.query(User).filter(User.username == "testuser").first()
    if not test_user:
        test_user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password=get_password_hash("testpass123"),
            role="admin",
            is_active=True
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✓ Created test user: {test_user.username}")
    else:
        print(f"✓ Test user exists: {test_user.username}")
    
    # Get or create test patient
    test_patient = db.query(Patient).filter(Patient.patient_id == "PAT-001").first()
    if not test_patient:
        test_patient = Patient(
            patient_id="PAT-001",
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime(1970, 5, 15).date(),
            gender="M",
            email="john.doe@example.com",
            phone="555-0100",
            address="123 Main St, Springfield, IL 62701"
        )
        db.add(test_patient)
        db.commit()
        db.refresh(test_patient)
        print(f"✓ Created test patient: {test_patient.first_name} {test_patient.last_name}")
    else:
        print(f"✓ Test patient exists: {test_patient.first_name} {test_patient.last_name}")
    
    # Create a COMPLETE CLAIM with all required fields (should pass validation)
    complete_claim = db.query(Claim).filter(Claim.claim_number == "CLM-COMPLETE-001").first()
    if not complete_claim:
        complete_claim = Claim(
            patient_id=test_patient.id,
            claim_number="CLM-COMPLETE-001",
            insurance_provider="BlueCross BlueShield",
            policy_number="POL-123456789",
            rendering_provider_npi="1234567890",  # Valid NPI format
            place_of_service="11",  # Office
            status=ClaimStatus.DRAFT,
            total_amount=300.0,
            created_by=test_user.id
        )
        db.add(complete_claim)
        db.commit()
        db.refresh(complete_claim)
        print(f"\n✓ Created COMPLETE claim: {complete_claim.claim_number}")
        print(f"  NPI: {complete_claim.rendering_provider_npi}")
        print(f"  Place of Service: {complete_claim.place_of_service} (Office)")
        
        # Add complete claim items with all required fields
        service_date = datetime.now() - timedelta(days=7)
        
        item1 = ClaimItem(
            claim_id=complete_claim.id,
            code_id=None,
            service_date_start=service_date,
            service_date_end=service_date,
            procedure_code="99213",
            diagnosis_code="Z00.00",  # ICD-10: Encounter for general adult medical examination
            amount=125.00,
            quantity=1,
            units="1",
            description="Office visit - Established patient, low complexity"
        )
        db.add(item1)
        
        item2 = ClaimItem(
            claim_id=complete_claim.id,
            code_id=None,
            service_date_start=service_date,
            service_date_end=service_date,
            procedure_code="99000",
            diagnosis_code="R51.9",  # ICD-10: Headache, unspecified
            amount=175.00,
            quantity=1,
            units="1",
            description="Evaluation and Management - Follow-up"
        )
        db.add(item2)
        
        db.commit()
        db.refresh(complete_claim)
        print(f"  Items: {len(complete_claim.claim_items)} added")
        print(f"  Total: ${complete_claim.total_amount:.2f}")
    else:
        print(f"✓ Complete claim already exists: {complete_claim.claim_number}")
    
    # Create a MINIMAL CLAIM (will show validation errors)
    minimal_claim = db.query(Claim).filter(Claim.claim_number == "CLM-MINIMAL-001").first()
    if not minimal_claim:
        minimal_claim = Claim(
            patient_id=test_patient.id,
            claim_number="CLM-MINIMAL-001",
            insurance_provider="Blue Shield",
            policy_number="POL-987654",
            # Missing: rendering_provider_npi, place_of_service
            status=ClaimStatus.DRAFT,
            total_amount=150.0,
            created_by=test_user.id
        )
        db.add(minimal_claim)
        db.commit()
        db.refresh(minimal_claim)
        print(f"\n✓ Created MINIMAL claim (for validation testing): {minimal_claim.claim_number}")
        
        # Add minimal items (missing procedure codes, diagnosis codes)
        item = ClaimItem(
            claim_id=minimal_claim.id,
            code_id=None,
            service_date_start=datetime.now() - timedelta(days=5),
            service_date_end=None,
            procedure_code=None,  # Missing
            diagnosis_code=None,  # Missing
            amount=150.00,
            quantity=1,
            description="Some medical service"
        )
        db.add(item)
        
        db.commit()
        db.refresh(minimal_claim)
        print(f"  Items: {len(minimal_claim.claim_items)} added (minimal data)")
    else:
        print(f"✓ Minimal claim already exists: {minimal_claim.claim_number}")
    
    print("\n" + "="*60)
    print("CLAIM URLS:")
    print("="*60)
    print(f"✓ Complete Claim (well-formed): http://localhost:5173/claims/{complete_claim.id}")
    print(f"✓ Minimal Claim (validation test): http://localhost:5173/claims/{minimal_claim.id}")
    print("="*60)
    
    db.close()
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
