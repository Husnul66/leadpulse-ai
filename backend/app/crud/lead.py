import logging
from typing import List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate

logger = logging.getLogger(__name__)


def get_lead(db: Session, lead_id: int) -> Optional[Lead]:
    """
    Retrieve a single lead by its unique primary key ID.
    
    :param db: SQLAlchemy database session.
    :param lead_id: Primary key ID of the lead.
    :return: Lead instance if found, None otherwise.
    """
    return db.query(Lead).filter(Lead.id == lead_id).first()


def get_leads(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
) -> List[Lead]:
    """
    Retrieve a paginated list of leads, optionally filtered by outreach status.
    
    :param db: SQLAlchemy database session.
    :param skip: Number of records to skip for pagination.
    :param limit: Maximum number of records to return.
    :param status: Optional status filter ("pending", "generated", "sent").
    :return: List of Lead model instances ordered from newest to oldest.
    """
    query = db.query(Lead)
    if status is not None:
        query = query.filter(Lead.status == status)
    return query.order_by(Lead.created_at.desc(), Lead.id.desc()).offset(skip).limit(limit).all()


def create_lead(db: Session, lead_in: LeadCreate) -> Lead:
    """
    Create a new lead entry in the database.
    
    :param db: SQLAlchemy database session.
    :param lead_in: LeadCreate Pydantic schema with prospect data.
    :return: Newly created and refreshed Lead model instance.
    """
    status_val = lead_in.status.value if hasattr(lead_in.status, "value") else (lead_in.status or "pending")
    
    db_lead = Lead(
        company_name=lead_in.company_name,
        company_url=str(lead_in.company_url),
        target_audience=lead_in.target_audience,
        status=status_val,
    )
    
    try:
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)
        return db_lead
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"Failed to create lead '{lead_in.company_name}': {exc}")
        raise


def update_lead(db: Session, db_lead: Lead, lead_in: Union[LeadUpdate, dict]) -> Lead:
    """
    Update an existing lead's fields using partial updates (PATCH / PUT).
    
    :param db: SQLAlchemy database session.
    :param db_lead: Existing Lead database entity to update.
    :param lead_in: LeadUpdate schema or dictionary containing modified fields.
    :return: Updated and refreshed Lead model instance.
    """
    if isinstance(lead_in, dict):
        update_data = lead_in
    else:
        update_data = lead_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "status" and hasattr(value, "value"):
            value = value.value
        elif field == "company_url" and value is not None:
            value = str(value)
        setattr(db_lead, field, value)

    try:
        db.commit()
        db.refresh(db_lead)
        return db_lead
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"Failed to update lead ID {db_lead.id}: {exc}")
        raise


def delete_lead(db: Session, lead_id: int) -> Optional[Lead]:
    """
    Delete a lead by its primary key ID. Any related generated messages
    are cascaded automatically by foreign key definition.
    
    :param db: SQLAlchemy database session.
    :param lead_id: Primary key ID of the lead to delete.
    :return: The deleted Lead instance if found, None if lead didn't exist.
    """
    db_lead = get_lead(db, lead_id)
    if not db_lead:
        return None

    try:
        db.delete(db_lead)
        db.commit()
        return db_lead
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"Failed to delete lead ID {lead_id}: {exc}")
        raise
