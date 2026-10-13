from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# Engine configuration
# pool_pre_ping=True helps detect and recycle severed connections (crucial for Supabase transaction / session poolers)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# SessionLocal class for instantiating database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Declarative Base for ORM models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency yielding a database session per request lifecycle.
    Ensures that the session is closed cleanly when the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
