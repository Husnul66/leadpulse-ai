from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """
    Basic health check endpoint returning API status.
    """
    return {
        "status": "healthy",
        "service": "LeadPulse AI Backend",
        "version": "0.1.0",
    }


@router.get("/health/db", status_code=status.HTTP_200_OK)
def database_health_check(db: Session = Depends(get_db)):
    """
    Database connection verification endpoint.
    Performs a lightweight 'SELECT 1' test on PostgreSQL / Supabase.
    """
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
        }
    except Exception as exc:
        return {
            "status": "unhealthy",
            "database": f"connection failed: {str(exc)}",
        }
