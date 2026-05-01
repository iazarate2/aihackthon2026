"""Pydantic models for RefCheck AI basketball review API."""

from typing import Optional

from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    """Body fields for POST /review (sent alongside optional file upload)."""

    original_call: str  # "Charge", "Blocking Foul", or "No Call"
    sample_case_id: Optional[str] = None


class RuleReference(BaseModel):
    title: str
    summary: str
    source_label: Optional[str] = None
    source_url: Optional[str] = None
    video_rulebook_url: Optional[str] = None


class RetrievedRule(BaseModel):
    id: str
    title: str
    summary: str
    source_label: Optional[str] = None
    source_url: Optional[str] = None
    video_rulebook_url: Optional[str] = None
    score: int


class ReviewResponse(BaseModel):
    verdict: str  # "Fair Call", "Bad Call", "Inconclusive"
    challenge_recommendation: str  # "Uphold Call", "Overturn Call", "Stands as Called"
    confidence: float
    original_call: str
    predicted_call: str
    review_type: str  # always "Charge vs. Block"
    evidence: list[str]
    rule_reference: RuleReference
    play_description: Optional[str] = None
    retrieved_rules: list[RetrievedRule] = Field(default_factory=list)
    cited_rules: list[RetrievedRule] = Field(default_factory=list)
    key_frames: list[str]
    limitations: list[str]
