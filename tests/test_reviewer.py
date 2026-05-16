from app.reviewer import review_resume


def test_demo_review_without_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    review = review_resume("Built APIs with Python and improved performance by 30%.")

    assert review.ai_enabled is False
    assert "GEMINI_API_KEY" in review.summary
    assert review.improvements
