#!/usr/bin/env python3
"""Initialize database and create a test user for development."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.db.database import engine, Base
from app.models.user import User
from app.db.database import SessionLocal
from app.core.security import get_password_hash
from sqlalchemy.orm import Session

def init_db():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")

def create_test_user(db: Session):
    """Create a test user for development."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == "admin").first()
    if existing_user:
        print("✓ Test user 'admin' already exists")
        return

    # Create test user
    test_user = User(
        username="admin",
        email="admin@example.com",
        full_name="Admin User",
        hashed_password=get_password_hash("admin123"),
        role="admin",
        is_active=True
    )
    
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    print(f"✓ Test user created: admin / admin123")
    print(f"  ID: {test_user.id}")
    print(f"  Email: {test_user.email}")
    print(f"  Role: {test_user.role}")

if __name__ == "__main__":
    print("🔧 Initializing Medical Coding & Claims Automation System...\n")
    
    try:
        # Initialize database
        init_db()
        
        # Create test user
        db = SessionLocal()
        try:
            create_test_user(db)
        finally:
            db.close()
        
        print("\n✅ Database initialization complete!")
        print("\n📝 Login credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n🌐 Frontend: http://localhost:5173")
        print("📚 API Docs: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
