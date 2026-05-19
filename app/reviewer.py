import json
import os
import time
from collections.abc import Iterator

from google import genai

from app.memory import add_turn, get_history
from app.schemas import ChatResponse, ReviewResponse


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


def stream_resume_review(resume_text: str, target_role: str | None = None) -> Iterator[str]:
    if not ai_is_configured():
        yield from simple_demo_stream(resume_text)
        return

    client = genai.Client()
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    prompt = f"""
Review this resume for a {target_role or "software job"}.

Stream the response in this readable format:

Summary:
- ...

Strengths:
- ...
- ...
- ...

Improvements:
- ...
- ...
- ...

Improved Summary:
...

Keep it concise and beginner-friendly.
Use short lines so the stream feels active in the UI.

Resume:
{resume_text}
"""

    response = client.models.generate_content_stream(
        model=model,
        contents=prompt,
    )

    for chunk in response:
        if chunk.text:
            yield from _small_stream_chunks(chunk.text)


def chat_with_memory(message: str, session_id: str = "demo") -> ChatResponse:
    answer = "".join(stream_chat_with_memory(message, session_id))

    return ChatResponse(
        ai_enabled=ai_is_configured(),
        session_id=session_id,
        answer=answer,
    )


def stream_chat_with_memory(message: str, session_id: str = "demo") -> Iterator[str]:
    add_turn(session_id, "user", message)

    if not ai_is_configured():
        answer = (
            "Demo memory answer. Add GEMINI_API_KEY to use Gemini.\n\n"
            f"I remembered your latest message in session '{session_id}': {message}"
        )
        add_turn(session_id, "assistant", answer)
        yield from _small_stream_chunks(answer, delay_seconds=0.04)
        return

    client = genai.Client()
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    prompt = _build_memory_prompt(session_id)
    answer_parts: list[str] = []

    response = client.models.generate_content_stream(
        model=model,
        contents=prompt,
    )

    for chunk in response:
        if chunk.text:
            answer_parts.append(chunk.text)
            yield from _small_stream_chunks(chunk.text)

    add_turn(session_id, "assistant", "".join(answer_parts))


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


def simple_demo_stream(resume_text: str) -> Iterator[str]:
    word_count = len(resume_text.split())
    chunks = [
        "Demo streaming review\n\n",
        f"Resume length: {word_count} words.\n\n",
        "Strengths:\n",
        "- You provided enough text to test the API flow.\n\n",
        "Improvements:\n",
        "- Add GEMINI_API_KEY to stream a real Gemini response.\n",
        "- Add metrics like 'improved speed by 30%'.\n",
        "- Include skills that match the target role.\n\n",
        "Improved Summary:\n",
        "Add your API key to generate a polished AI-written summary.",
    ]

    for chunk in chunks:
        yield from _small_stream_chunks(chunk, delay_seconds=0.04)


def _small_stream_chunks(
    text: str,
    size: int = 8,
    delay_seconds: float = 0.015,
) -> Iterator[str]:
    for index in range(0, len(text), size):
        time.sleep(delay_seconds)
        yield text[index : index + size]


def _build_memory_prompt(session_id: str) -> str:
    history = get_history(session_id)
    lines = [
        "You are a helpful resume coach chatbot.",
        "Use the conversation history to answer follow-up questions.",
        "Keep answers concise and beginner-friendly.",
        "",
        "Conversation history:",
    ]

    for turn in history:
        lines.append(f"{turn['role'].title()}: {turn['text']}")

    return "\n".join(lines)


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
