from app.db.database import SessionLocal
from app.schemas.user import UserCreate
from app.api.auth import register

if __name__ == '__main__':
    db = SessionLocal()
    user = UserCreate(
        username='tempuser123',
        password='TempPass123!',
        email='tempuser123@example.com',
        full_name='Temp User',
        role='viewer'
    )
    try:
        result = register(user, db)
        print('RESULT:', result)
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        db.close()
