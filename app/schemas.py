from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    resume_text: str = Field(..., min_length=20)
    target_role: str | None = None


class ReviewResponse(BaseModel):
    ai_enabled: bool
    summary: str
    strengths: list[str]
    improvements: list[str]
    improved_summary: str
