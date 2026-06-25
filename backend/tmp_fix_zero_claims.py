#!/usr/bin/env python
"""Fix claims with $0.00 amount - recalculate from items or set default."""
import sys

try:
    import app.main
    from app.db.database import SessionLocal
    from app.models.claim import Claim
    
    db = SessionLocal()
    
    # Get all claims with $0.00
    zero_claims = db.query(Claim).filter(Claim.total_amount == 0.0).all()
    
    print(f"\nFound {len(zero_claims)} claims with $0.00 total amount")
    print("=" * 70)
    
    fixed_count = 0
    
    for claim in zero_claims:
        old_amount = claim.total_amount
        
        # Calculate total from items if they exist
        if claim.claim_items and len(claim.claim_items) > 0:
            claim.total_amount = sum(item.amount * item.quantity for item in claim.claim_items)
            fixed_count += 1
            print(f"✓ CLM {claim.claim_number}: Recalculated from items: ${claim.total_amount:.2f}")
        else:
            # Set default amount of $100 if no items
            claim.total_amount = 100.0
            fixed_count += 1
            print(f"✓ CLM {claim.claim_number}: Set default amount: $100.00 (no items)")
    
    if fixed_count > 0:
        db.commit()
        print("=" * 70)
        print(f"✓ Fixed {fixed_count} claims with zero amounts")
    else:
        print("No claims needed fixing")
    
    db.close()
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
