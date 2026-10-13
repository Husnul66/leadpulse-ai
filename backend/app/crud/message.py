import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.message import GeneratedMessage
from app.schemas.message import GeneratedMessageCreate

logger = logging.getLogger(__name__)


def create_generated_message(db: Session, message_in: GeneratedMessageCreate) -> GeneratedMessage:
    """
    Persists a newly generated outreach message associated with a lead.
    
    :param db: SQLAlchemy database session.
    :param message_in: GeneratedMessageCreate schema containing lead_id, channel, and content.
    :return: Refreshed GeneratedMessage ORM model instance.
    """
    db_message = GeneratedMessage(
        lead_id=message_in.lead_id,
        outreach_channel=message_in.outreach_channel,
        generated_content=message_in.generated_content,
    )
    try:
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"Failed to persist generated message for lead ID {message_in.lead_id}: {exc}")
        raise


def get_messages_by_lead_id(db: Session, lead_id: int) -> List[GeneratedMessage]:
    """
    Retrieves all generated messages for a given lead, ordered from newest to oldest.
    
    :param db: SQLAlchemy database session.
    :param lead_id: Target lead ID.
    :return: List of GeneratedMessage ORM model instances.
    """
    return (
        db.query(GeneratedMessage)
        .filter(GeneratedMessage.lead_id == lead_id)
        .order_by(GeneratedMessage.created_at.desc(), GeneratedMessage.id.desc())
        .all()
    )


def get_message_by_id(db: Session, message_id: int) -> Optional[GeneratedMessage]:
    """
    Retrieves a single generated message by primary key ID.
    
    :param db: SQLAlchemy database session.
    :param message_id: Target message ID.
    :return: GeneratedMessage instance if found, None otherwise.
    """
    return db.query(GeneratedMessage).filter(GeneratedMessage.id == message_id).first()


def delete_message_by_id(db: Session, message_id: int) -> Optional[GeneratedMessage]:
    """
    Deletes a generated message by primary key ID.
    
    :param db: SQLAlchemy database session.
    :param message_id: Target message ID.
    :return: Deleted GeneratedMessage instance if found, None otherwise.
    """
    message = get_message_by_id(db, message_id)
    if not message:
        return None
    try:
        db.delete(message)
        db.commit()
        return message
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"Failed to delete generated message ID {message_id}: {exc}")
        raise
