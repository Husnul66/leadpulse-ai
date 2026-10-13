from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.lead import Lead
from app.models.message import GeneratedMessage
from app.schemas.message import GeneratedMessageCreate, GeneratedMessageResponse

router = APIRouter(prefix="/messages", tags=["Generated Messages"])


@router.post("/", response_model=GeneratedMessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(message_in: GeneratedMessageCreate, db: Session = Depends(get_db)):
    """
    Store an AI-generated message for a lead.
    """
    # Verify lead exists
    lead = db.query(Lead).filter(Lead.id == message_in.lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot associate message: Lead with ID {message_in.lead_id} not found",
        )

    message = GeneratedMessage(
        lead_id=message_in.lead_id,
        outreach_channel=message_in.outreach_channel,
        generated_content=message_in.generated_content,
    )
    db.add(message)

    # Automatically transition lead status to 'generated' if it was 'pending'
    if lead.status == "pending":
        lead.status = "generated"

    db.commit()
    db.refresh(message)
    return message


@router.get("/lead/{lead_id}", response_model=List[GeneratedMessageResponse])
def get_messages_by_lead(lead_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all generated messages for a given lead.
    """
    messages = (
        db.query(GeneratedMessage)
        .filter(GeneratedMessage.lead_id == lead_id)
        .order_by(GeneratedMessage.created_at.desc())
        .all()
    )
    return messages
