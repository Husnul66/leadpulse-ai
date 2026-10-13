from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.schemas.message import (
    MessageGenerateRequest,
    GeneratedMessageCreate,
    GeneratedMessageResponse,
)
from app.crud import lead as crud_lead
from app.crud import message as crud_message
from app.services.ai_service import (
    generate_outreach_message,
    AIConfigurationError,
    AIRateLimitError,
    AIServiceError,
)

router = APIRouter(prefix="/leads", tags=["Outreach Messages"])


@router.post(
    "/{lead_id}/generate",
    response_model=GeneratedMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate personalized outreach message with Gemini AI",
    description=(
        "Invokes the Google Gemini AI model to generate a tailored B2B outreach copy "
        "for the specified lead, stores the generated message in the database, and transitions "
        "the lead status to 'generated'."
    ),
)
def generate_message_for_lead(
    lead_id: int = Path(..., ge=1, description="Primary key ID of the target lead"),
    generate_request: MessageGenerateRequest = MessageGenerateRequest(),
    db: Session = Depends(get_db),
):
    """
    Generate and persist an AI-crafted outreach message for a prospect lead.
    
    :param lead_id: Unique identifier of the prospect lead.
    :param generate_request: Channel, sender information, and optional custom prompt instructions.
    :param db: SQLAlchemy database session.
    :return: The created GeneratedMessage record with assigned ID and timestamp.
    """
    # 1. Fetch target lead
    db_lead = crud_lead.get_lead(db=db, lead_id=lead_id)
    if not db_lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with ID {lead_id} not found.",
        )

    # 2. Invoke Gemini AI Service
    channel_str = (
        generate_request.outreach_channel.value
        if hasattr(generate_request.outreach_channel, "value")
        else str(generate_request.outreach_channel)
    )

    try:
        generated_copy = generate_outreach_message(
            company_name=db_lead.company_name,
            company_url=db_lead.company_url,
            target_audience=db_lead.target_audience,
            channel=channel_str,
            sender_name=generate_request.sender_name,
            sender_company=generate_request.sender_company,
            value_proposition=generate_request.value_proposition,
            additional_instructions=generate_request.additional_instructions,
        )
    except AIConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
    except AIRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        )
    except AIServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service provider error: {str(exc)}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during message generation: {str(exc)}",
        )

    # 3. Persist the generated message to database
    try:
        msg_in = GeneratedMessageCreate(
            lead_id=db_lead.id,
            outreach_channel=channel_str,
            generated_content=generated_copy,
        )
        saved_message = crud_message.create_generated_message(db=db, message_in=msg_in)

        # Automatically transition lead status to 'generated' if it was 'pending'
        if db_lead.status == "pending":
            crud_lead.update_lead(db=db, db_lead=db_lead, lead_in={"status": "generated"})

        return saved_message

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error saving generated message: {str(exc)}",
        )


@router.get(
    "/{lead_id}/messages",
    response_model=List[GeneratedMessageResponse],
    status_code=status.HTTP_200_OK,
    summary="List outreach messages for a lead",
    description="Fetches all previously generated outreach message copies associated with a specific lead.",
)
def get_messages_for_lead(
    lead_id: int = Path(..., ge=1, description="Primary key ID of the target lead"),
    db: Session = Depends(get_db),
):
    """
    Retrieve message generation history for a given lead.
    
    :param lead_id: Unique identifier of the prospect lead.
    :param db: SQLAlchemy database session.
    :return: List of GeneratedMessage records.
    """
    db_lead = crud_lead.get_lead(db=db, lead_id=lead_id)
    if not db_lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with ID {lead_id} not found.",
        )

    messages = crud_message.get_messages_by_lead_id(db=db, lead_id=lead_id)
    return messages
