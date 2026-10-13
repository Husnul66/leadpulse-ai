from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class GeneratedMessageBase(BaseModel):
    lead_id: int = Field(..., description="Referenced lead ID", example=1)
    outreach_channel: str = Field(..., description="Channel name: e.g. cold_email, linkedin", example="cold_email")
    generated_content: str = Field(..., description="AI generated outreach message content")


class GeneratedMessageCreate(GeneratedMessageBase):
    pass


class GeneratedMessageResponse(GeneratedMessageBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
