from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class LeadBase(BaseModel):
    company_name: str = Field(..., description="Name of the prospect company", example="Acme Corp")
    company_url: str = Field(..., description="Website URL of the company", example="https://acme.example.com")
    target_audience: Optional[str] = Field(None, description="Target customer segment or ICP", example="B2B SaaS Founders")
    status: Optional[str] = Field("pending", description="Lead status: pending, generated, sent", example="pending")


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    company_name: Optional[str] = None
    company_url: Optional[str] = None
    target_audience: Optional[str] = None
    status: Optional[str] = None


class LeadResponse(LeadBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
