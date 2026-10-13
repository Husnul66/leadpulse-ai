from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class GeneratedMessage(Base):
    """
    GeneratedMessage model representing AI-crafted outreach copy for a specific lead and channel.
    """
    __tablename__ = "generated_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lead_id = Column(
        Integer,
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    outreach_channel = Column(String(50), nullable=False)  # e.g., "cold_email", "linkedin"
    generated_content = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    # Relationships
    lead = relationship("Lead", back_populates="messages")

    def __repr__(self) -> str:
        return f"<GeneratedMessage(id={self.id}, lead_id={self.lead_id}, outreach_channel='{self.outreach_channel}')>"
