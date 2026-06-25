#!/usr/bin/env python
"""Check claims in the database and their validation status."""
import os
import sys

# Ensure app imports work
try:
    from app.models.claim import Claim, ClaimValidation
    from app.models.patient import Patient
    from app.models.user import User
    from app.db.database import SessionLocal

    db = SessionLocal()
    
    # Check total claims
    total_claims = db.query(Claim).count()
    print(f"Total claims in DB: {total_claims}")
    
    if total_claims == 0:
        print("No claims found. Database is empty.")
    else:
        # List first 5 claims with details
        claims = db.query(Claim).limit(5).all()
        for claim in claims:
            print(f"\n--- Claim ID {claim.id} ---")
            print(f"  Claim Number: {claim.claim_number}")
            print(f"  Status: {claim.status}")
            print(f"  Patient ID: {claim.patient_id}")
            print(f"  Total Amount: ${claim.total_amount}")
            print(f"  Items: {len(claim.claim_items)}")
            print(f"  Validations: {len(claim.validations)}")
            if claim.validations:
                for v in claim.validations:
                    print(f"    - {v.validation_type} ({v.severity}): {v.error_message}")
    
    db.close()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
