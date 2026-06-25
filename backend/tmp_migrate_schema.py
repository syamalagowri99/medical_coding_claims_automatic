#!/usr/bin/env python
"""Add new columns to claims and claim_items tables."""
import sys

try:
    from sqlalchemy import text
    from app.db.database import SessionLocal, engine
    
    db = SessionLocal()
    
    print("Adding new columns to claims table...")
    try:
        db.execute(text("ALTER TABLE claims ADD COLUMN rendering_provider_npi VARCHAR"))
        db.execute(text("ALTER TABLE claims ADD COLUMN place_of_service VARCHAR"))
        db.commit()
        print("✓ Added columns to claims table")
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
            print("✓ Columns already exist in claims table")
        else:
            raise
    
    print("Adding new columns to claim_items table...")
    try:
        db.execute(text("ALTER TABLE claim_items ADD COLUMN service_date_start TIMESTAMP WITH TIME ZONE"))
        db.execute(text("ALTER TABLE claim_items ADD COLUMN service_date_end TIMESTAMP WITH TIME ZONE"))
        db.execute(text("ALTER TABLE claim_items ADD COLUMN procedure_code VARCHAR"))
        db.execute(text("ALTER TABLE claim_items ADD COLUMN diagnosis_code VARCHAR"))
        db.execute(text("ALTER TABLE claim_items ADD COLUMN units VARCHAR"))
        db.commit()
        print("✓ Added columns to claim_items table")
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
            print("✓ Columns already exist in claim_items table")
        else:
            raise
    
    print("\n✓ Database schema updated successfully!")
    db.close()
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
