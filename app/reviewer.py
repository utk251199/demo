import json
import os

from google import genai

from app.schemas import ReviewResponse


def ai_is_configured() -> bool:
    return bool(os.getenv("GEMINI_API_KEY"))


def review_resume(resume_text: str, target_role: str | None = None) -> ReviewResponse:
    if not ai_is_configured():
        return simple_demo_review(resume_text)

    client = genai.Client()
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    prompt = f"""
Review this resume for a {target_role or "software job"}.

Return only valid JSON using exactly this shape:

{{
  "summary": "Two short sentences.",
  "strengths": ["Strength 1", "Strength 2", "Strength 3"],
  "improvements": ["Improvement 1", "Improvement 2", "Improvement 3"],
  "improved_summary": "One polished resume summary paragraph."
}}

Rules:
- Be concise.
- Do not include Markdown.
- Do not include text before or after the JSON.
- Use exactly 3 strengths and 3 improvements.
- Keep the tone practical and beginner-friendly.

Resume:
{resume_text}
"""

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    return _parse_gemini_review(response.text or "")


def simple_demo_review(resume_text: str) -> ReviewResponse:
    word_count = len(resume_text.split())

    return ReviewResponse(
        ai_enabled=False,
        summary="Demo review only. Add GEMINI_API_KEY to use the Gemini model.",
        strengths=[f"Resume length is {word_count} words."],
        improvements=[
            "Add numbers to show impact, like 'improved speed by 30%'.",
            "Start bullets with action verbs like built, led, shipped, or improved.",
            "Include skills that match the job description.",
        ],
        improved_summary="Add your API key to generate a polished AI-written resume summary.",
    )


def _parse_gemini_review(text: str) -> ReviewResponse:
    cleaned_text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        data = json.loads(cleaned_text)
    except json.JSONDecodeError:
        data = {}

    return ReviewResponse(
        ai_enabled=True,
        summary=data.get("summary") or "Gemini returned a review, but it was not valid JSON.",
        strengths=data.get("strengths") or [],
        improvements=data.get("improvements") or [text.strip()],
        improved_summary=data.get("improved_summary") or "",
    )
