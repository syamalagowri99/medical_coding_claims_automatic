from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from app.core.config import settings


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user."""
    # Check if email already exists
    if db.query(User).filter(User.email == user.email).first():
        raise ValueError("Email already registered")
    
    # Check if username already exists
    if db.query(User).filter(User.username == user.username).first():
        raise ValueError("Username already taken")

    if len(user.password.encode('utf-8')) > 72:
        raise ValueError("Password cannot be longer than 72 bytes. Please choose a shorter password.")
    
    # Create user with hashed password
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str) -> User:
    """Authenticate user with username and password."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def login_user(db: Session, username: str, password: str) -> tuple[str, User]:
    """Login user and return access token."""
    user = authenticate_user(db, username, password)
    if not user:
        raise ValueError("Invalid username or password")
    
    if not user.is_active:
        raise ValueError("User account is inactive")
    
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return access_token, user


def get_user_by_id(db: Session, user_id: int) -> User:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
    """Update user information."""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise ValueError("User not found")
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user
