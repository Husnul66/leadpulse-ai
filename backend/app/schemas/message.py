from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class OutreachChannel(str, Enum):
    """Supported outreach communication channels."""
    COLD_EMAIL = "cold_email"
    LINKEDIN = "linkedin"
    TWITTER_DM = "twitter_dm"


class MessageGenerateRequest(BaseModel):
    """Request payload for triggering AI outreach message generation."""
    outreach_channel: OutreachChannel = Field(
        default=OutreachChannel.COLD_EMAIL,
        description="The desired target channel for the generated outreach message",
        examples=["cold_email"],
    )
    sender_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Name of the sender to sign the message with",
        examples=["Alex Morgan"],
    )
    sender_company: Optional[str] = Field(
        default=None,
        max_length=150,
        description="Name of the sender's company offering the solution",
        examples=["LeadPulse AI"],
    )
    value_proposition: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Core value proposition, pain point addressed, or key offering highlights",
        examples=["We help B2B teams triple outbound meeting booking rates via automated personalization."],
    )
    additional_instructions: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Additional context, tone preferences, or specific call-to-action (CTA)",
        examples=["Keep it under 100 words with a casual and conversational tone."],
    )


class GeneratedMessageBase(BaseModel):
    """Base schema for generated outreach messages."""
    lead_id: int = Field(..., description="Foreign key referencing the target Lead ID", examples=[1])
    outreach_channel: str = Field(..., description="Channel name (e.g. cold_email, linkedin)", examples=["cold_email"])
    generated_content: str = Field(..., description="AI-generated personalized message body")


class GeneratedMessageCreate(GeneratedMessageBase):
    """Schema used when persisting an outreach message to the database."""
    pass


class GeneratedMessageResponse(GeneratedMessageBase):
    """Output schema returned to API clients representing a stored message."""
    id: int = Field(..., description="Unique primary key identifier for the generated message")
    created_at: datetime = Field(..., description="UTC creation timestamp")

    model_config = ConfigDict(from_attributes=True)
