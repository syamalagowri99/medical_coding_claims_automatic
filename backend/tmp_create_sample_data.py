#!/usr/bin/env python
"""Create sample test data for the medical coding app."""
import sys
from datetime import datetime, timedelta

try:
    # Import the main app first to ensure all models are registered
    import app.main
    from app.db.database import SessionLocal
    from app.models.user import User
    from app.models.patient import Patient
    from app.models.claim import Claim, ClaimStatus, ClaimItem
    from app.models.medical_code import MedicalCode, CodeStatus
    from app.core.security import get_password_hash
    
    db = SessionLocal()
    
    # Create test user
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
        print(f"✓ Test user already exists: {test_user.username}")
    
    # Create test patient
    test_patient = db.query(Patient).filter(Patient.first_name == "John").first()
    if not test_patient:
        test_patient = Patient(
            patient_id="PAT-001",
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime(1980, 1, 15).date(),
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
        print(f"✓ Test patient already exists: {test_patient.first_name} {test_patient.last_name}")
    
    # Create test medical codes
    created_codes = []
    # Skip medical codes for now - they require ExtractedEntity which is complex
    
    # Create test claim
    test_claim = db.query(Claim).filter(Claim.claim_number == "CLM-TEST-001").first()
    if not test_claim:
        test_claim = Claim(
            patient_id=test_patient.id,
            claim_number="CLM-TEST-001",
            insurance_provider="BlueCross BlueShield",
            policy_number="POL-123456",
            status=ClaimStatus.DRAFT,
            total_amount=300.0,
            created_by=test_user.id
        )
        db.add(test_claim)
        db.commit()
        db.refresh(test_claim)
        print(f"✓ Created test claim: {test_claim.claim_number}")
        
        # Add simple claim items without medical codes
        item1 = ClaimItem(
            claim_id=test_claim.id,
            code_id=None,
            service_date=datetime.now() - timedelta(days=5),
            amount=150.00,
            quantity=1,
            description="Office visit - established patient (CPT 99213)"
        )
        db.add(item1)
        
        item2 = ClaimItem(
            claim_id=test_claim.id,
            code_id=None,
            service_date=datetime.now() - timedelta(days=5),
            amount=150.00,
            quantity=1,
            description="Head CT without contrast (CPT 70450)"
        )
        db.add(item2)
        
        db.commit()
        db.refresh(test_claim)
        print(f"✓ Added 2 items to claim")
    else:
        print(f"✓ Test claim already exists: {test_claim.claim_number}")
        created_codes = []
    
    print("\n✓ Sample data created successfully!")
    print(f"Test claim ID: {test_claim.id}")
    print(f"You can now access: http://localhost:5173/claims/{test_claim.id}")
    
    db.close()
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
