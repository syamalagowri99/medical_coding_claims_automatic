from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Database engine (SQLite for local development, PostgreSQL for production)
connect_args = {}
if settings.DATABASE_URL.startswith("postgresql"):
    connect_args = {"connect_timeout": 10}

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # Verify connections before using
    connect_args=connect_args
)

# Enable pgvector extension on connection (PostgreSQL only)
@event.listens_for(engine, "connect")
def load_pgvector(dbapi_conn, connection_record):
    """Load pgvector extension on database connection."""
    if settings.DATABASE_URL.startswith("postgresql"):
        try:
            cursor = dbapi_conn.cursor()
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            dbapi_conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Warning: Could not load pgvector extension: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
