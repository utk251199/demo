from dotenv import load_dotenv
from fastapi import FastAPI

from app.reviewer import ai_is_configured, review_resume
from app.schemas import ReviewRequest, ReviewResponse


load_dotenv()

app = FastAPI(title="Simple AI Resume Reviewer")


@app.get("/")
def home() -> dict[str, str | bool]:
    return {
        "message": "AI Resume Reviewer API is running",
        "ai_enabled": ai_is_configured(),
    }


@app.post("/review", response_model=ReviewResponse)
def review(request: ReviewRequest) -> ReviewResponse:
    return review_resume(
        resume_text=request.resume_text,
        target_role=request.target_role,
    )
