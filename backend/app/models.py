"""Pydantic models for RefCheck AI basketball review API."""

from pydantic import BaseModel


class ReviewRequest(BaseModel):
    """Body fields for POST /review (sent alongside optional file upload)."""

    original_call: str  # "Charge", "Blocking Foul", or "No Call"
    sample_case_id: str | None = None


class RuleReference(BaseModel):
    title: str
    summary: str


class ReviewResponse(BaseModel):
    verdict: str  # "Fair Call", "Bad Call", "Inconclusive"
    challenge_recommendation: str  # "Uphold Call", "Overturn Call", "Stands as Called"
    confidence: float
    original_call: str
    predicted_call: str
    review_type: str  # always "Charge vs. Block"
    evidence: list[str]
    rule_reference: RuleReference
    key_frames: list[str]
    limitations: list[str]
