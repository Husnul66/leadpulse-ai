from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class LeadStatus(str, Enum):
    """Enumeration of outreach statuses for a lead."""
    PENDING = "pending"
    GENERATED = "generated"
    SENT = "sent"


class LeadBase(BaseModel):
    """Base schema containing common attributes for a Lead."""
    company_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the prospect company",
        examples=["Acme Corp"],
    )
    company_url: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Website URL of the company",
        examples=["https://acme.example.com"],
    )
    target_audience: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Target customer segment, Ideal Customer Profile (ICP), or persona",
        examples=["B2B SaaS Founders & Sales Leaders"],
    )
    status: Optional[LeadStatus] = Field(
        default=LeadStatus.PENDING,
        description="Lead outreach pipeline status",
        examples=["pending"],
    )

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Company name cannot be blank or whitespace only")
        return trimmed

    @field_validator("company_url")
    @classmethod
    def validate_company_url(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Company URL cannot be blank or whitespace only")
        # Automatically prepend https:// if missing for better UX
        if not (trimmed.startswith("http://") or trimmed.startswith("https://")):
            trimmed = f"https://{trimmed}"
        return trimmed


class LeadCreate(LeadBase):
    """Schema for creating a new lead."""
    pass


class LeadUpdate(BaseModel):
    """Schema for updating an existing lead. All fields are optional."""
    company_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Updated company name",
        examples=["Acme Technologies"],
    )
    company_url: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=500,
        description="Updated company website URL",
        examples=["https://acme.tech"],
    )
    target_audience: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Updated target customer segment or ICP",
        examples=["Enterprise CTOs"],
    )
    status: Optional[LeadStatus] = Field(
        default=None,
        description="Updated lead pipeline status",
        examples=["generated"],
    )

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Company name cannot be blank")
            return trimmed
        return v

    @field_validator("company_url")
    @classmethod
    def validate_company_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Company URL cannot be blank")
            if not (trimmed.startswith("http://") or trimmed.startswith("https://")):
                trimmed = f"https://{trimmed}"
            return trimmed
        return v


class LeadResponse(LeadBase):
    """Schema for lead output responses serialized from ORM models."""
    id: int = Field(..., description="Unique database identifier for the lead")
    created_at: datetime = Field(..., description="UTC creation timestamp")

    model_config = ConfigDict(from_attributes=True)
