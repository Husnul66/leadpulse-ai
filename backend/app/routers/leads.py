from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.schemas.lead import (
    LeadCreate,
    LeadUpdate,
    LeadResponse,
    LeadStatus,
)
from app.crud import lead as crud_lead

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.post(
    "/",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new lead",
    description="Registers a new prospect lead with company name, URL, target audience, and initial status.",
)
def create_lead_endpoint(
    lead_in: LeadCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new lead record in the database.
    """
    try:
        new_lead = crud_lead.create_lead(db=db, lead_in=lead_in)
        return new_lead
    except SQLAlchemyError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while creating lead: {str(err)}",
        )


@router.get(
    "/",
    response_model=List[LeadResponse],
    status_code=status.HTTP_200_OK,
    summary="List all leads",
    description="Retrieve a paginated list of leads, optionally filtered by status (pending, generated, sent).",
)
def get_leads_endpoint(
    skip: int = Query(0, ge=0, description="Offset: number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Limit: maximum records to return"),
    status_filter: Optional[LeadStatus] = Query(None, alias="status", description="Filter by outreach status"),
    db: Session = Depends(get_db),
):
    """
    List leads with pagination and optional status filter.
    """
    try:
        filter_val = status_filter.value if status_filter else None
        leads = crud_lead.get_leads(db=db, skip=skip, limit=limit, status=filter_val)
        return leads
    except SQLAlchemyError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while fetching leads: {str(err)}",
        )


@router.get(
    "/{lead_id}",
    response_model=LeadResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single lead by ID",
    description="Fetch full details for a single prospect lead using its primary key ID.",
)
def get_lead_endpoint(
    lead_id: int = Path(..., ge=1, description="Primary key ID of the lead"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific lead by ID or return 404 if not found.
    """
    lead = crud_lead.get_lead(db=db, lead_id=lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with ID {lead_id} not found",
        )
    return lead


@router.put(
    "/{lead_id}",
    response_model=LeadResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a lead",
    description="Update an existing lead's company info, target audience, or status.",
)
@router.patch(
    "/{lead_id}",
    response_model=LeadResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,  # Expose PUT as primary in docs, keep PATCH as convenient alias
)
def update_lead_endpoint(
    lead_id: int = Path(..., ge=1, description="Primary key ID of the lead to update"),
    lead_in: LeadUpdate = ...,
    db: Session = Depends(get_db),
):
    """
    Update lead details (company name, URL, target audience, or status).
    Returns 404 if the lead does not exist.
    """
    db_lead = crud_lead.get_lead(db=db, lead_id=lead_id)
    if not db_lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with ID {lead_id} not found",
        )

    try:
        updated_lead = crud_lead.update_lead(db=db, db_lead=db_lead, lead_in=lead_in)
        return updated_lead
    except SQLAlchemyError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while updating lead ID {lead_id}: {str(err)}",
        )


@router.delete(
    "/{lead_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a lead",
    description="Delete a lead and cascade delete any associated generated outreach messages.",
)
def delete_lead_endpoint(
    lead_id: int = Path(..., ge=1, description="Primary key ID of the lead to delete"),
    db: Session = Depends(get_db),
):
    """
    Delete a lead by its ID. Returns 404 if the lead does not exist.
    """
    db_lead = crud_lead.get_lead(db=db, lead_id=lead_id)
    if not db_lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with ID {lead_id} not found",
        )

    try:
        crud_lead.delete_lead(db=db, lead_id=lead_id)
        return None
    except SQLAlchemyError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while deleting lead ID {lead_id}: {str(err)}",
        )
