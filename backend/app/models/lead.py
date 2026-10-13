from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Lead(Base):
    """
    Lead model representing a target company / prospect for outreach.
    """
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_name = Column(String(255), nullable=False, index=True)
    company_url = Column(String(500), nullable=False)
    target_audience = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default="pending")  # pending, generated, sent
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    # Relationships
    messages = relationship(
        "GeneratedMessage",
        back_populates="lead",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Lead(id={self.id}, company_name='{self.company_name}', status='{self.status}')>"
