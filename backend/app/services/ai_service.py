import logging
from typing import Optional
from google import genai
from google.genai import types, errors
from app.config import settings

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Base exception for AI generation service errors."""
    pass


class AIConfigurationError(AIServiceError):
    """Raised when the Gemini API key or necessary configuration is missing."""
    pass


class AIRateLimitError(AIServiceError):
    """Raised when the Gemini API rate limit or quota has been exceeded."""
    pass


def get_gemini_client() -> genai.Client:
    """
    Initializes and returns a Google GenAI Client instance using the configured API key.
    
    :raises AIConfigurationError: If GEMINI_API_KEY is not defined in settings.
    :return: An active google.genai.Client instance.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key or not api_key.strip():
        raise AIConfigurationError(
            "GEMINI_API_KEY is not configured. Please add your Gemini API key "
            "to the backend/.env file (e.g. GEMINI_API_KEY='your-key-here')."
        )
    return genai.Client(api_key=api_key.strip())


def build_outreach_prompt(
    company_name: str,
    company_url: str,
    target_audience: Optional[str] = None,
    channel: str = "cold_email",
    sender_name: Optional[str] = None,
    sender_company: Optional[str] = None,
    value_proposition: Optional[str] = None,
    additional_instructions: Optional[str] = None,
) -> str:
    """
    Constructs a highly tailored, context-rich prompt for Gemini to craft
    high-converting B2B cold outreach copy.
    """
    sender = sender_name or "Alex"
    company_offering = sender_company or "LeadPulse AI"
    value_prop = (
        value_proposition
        or "automating high-converting personalized outbound sales campaigns that boost reply rates"
    )
    audience = target_audience or "B2B leaders and key decision makers"

    if channel == "linkedin":
        format_guidelines = (
            "- Channel: LinkedIn Outreach Message / InMail\n"
            "- Length: Under 120 words (concise, conversational, non-spammy).\n"
            "- Structure: Warm personalized opener referencing their company, brief common ground/insight, "
            "one sentence on potential relevance, and a low-pressure open question."
        )
    elif channel == "twitter_dm":
        format_guidelines = (
            "- Channel: Twitter/X Direct Message\n"
            "- Length: Under 60 words (casual, peer-to-peer tone).\n"
            "- Structure: Quick relevant hook, concise insight, no corporate jargon."
        )
    else:  # Default to cold_email
        format_guidelines = (
            "- Channel: B2B Cold Email\n"
            "- Format: Start with 'Subject: [compelling 3-6 word subject line]' on the very first line.\n"
            "- Length: 75-130 words in total.\n"
            "- Structure: Personalized observation about their business -> Pain point/insight -> "
            "How our solution helps -> Soft, low-friction Call to Action (e.g., 'Open to exploring a brief 5-min demo next Tuesday?')."
        )

    prompt = f"""You are an elite B2B Sales Development Representative (SDR) and cold outreach copywriter.
Your task is to write a personalized, highly compelling outreach message to a prospect.

PROSPECT INFORMATION:
- Target Company Name: {company_name}
- Target Website / Domain: {company_url}
- Target Audience / ICP Segment: {audience}

SENDER INFORMATION:
- Sender Name: {sender}
- Sender Company: {company_offering}
- Value Proposition: {value_prop}

OUTREACH SPECIFICATIONS:
{format_guidelines}

ADDITIONAL CONSTRAINTS:
- Do not use cheesy buzzwords or clichés (avoid: 'Hope this finds you well', 'Synergy', 'Game changer', 'Quick question').
- Sound authentic, thoughtful, and research-backed.
- Output ONLY the final message copy without any meta-commentary, markdown fences, or preamble.
"""
    if additional_instructions:
        prompt += f"\nSPECIAL USER INSTRUCTIONS:\n- {additional_instructions}\n"

    return prompt


def generate_outreach_message(
    company_name: str,
    company_url: str,
    target_audience: Optional[str] = None,
    channel: str = "cold_email",
    sender_name: Optional[str] = None,
    sender_company: Optional[str] = None,
    value_proposition: Optional[str] = None,
    additional_instructions: Optional[str] = None,
) -> str:
    """
    Invokes the Google Gemini API to generate a personalized outreach message.
    
    :param company_name: Name of the prospect company.
    :param company_url: Website URL of the prospect company.
    :param target_audience: Target audience or persona description.
    :param channel: Outreach channel ('cold_email', 'linkedin', 'twitter_dm').
    :param sender_name: Sender's name.
    :param sender_company: Sender's company name.
    :param value_proposition: Solution value proposition.
    :param additional_instructions: Additional tone or prompt instructions.
    :raises AIConfigurationError: When the Gemini API key is not configured.
    :raises AIRateLimitError: When API rate limits are hit.
    :raises AIServiceError: When Gemini returns an API or networking error.
    :return: The generated message text.
    """
    client = get_gemini_client()
    prompt = build_outreach_prompt(
        company_name=company_name,
        company_url=company_url,
        target_audience=target_audience,
        channel=channel,
        sender_name=sender_name,
        sender_company=sender_company,
        value_proposition=value_proposition,
        additional_instructions=additional_instructions,
    )

    model_name = settings.GEMINI_MODEL or "gemini-2.5-flash"
    logger.info(f"Generating outreach message for '{company_name}' via Gemini model '{model_name}' (channel: {channel})")

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.95,
                max_output_tokens=800,
            ),
        )

        if not response or not response.text:
            raise AIServiceError("Gemini returned an empty response.")

        return response.text.strip()

    except errors.APIError as exc:
        logger.error(f"Gemini API Error: {exc}")
        if getattr(exc, "code", None) == 429:
            raise AIRateLimitError("Gemini API rate limit exceeded. Please try again in a few moments.") from exc
        raise AIServiceError(f"Gemini API Error ({getattr(exc, 'code', 'unknown')}): {exc.message}") from exc

    except Exception as exc:
        logger.error(f"Unexpected error communicating with Gemini API: {exc}")
        raise AIServiceError(f"Failed to generate message: {str(exc)}") from exc
