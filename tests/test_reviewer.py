from app.memory import clear_history, get_history
from app.reviewer import stream_chat_with_memory


def test_stream_chat_without_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    clear_history("test-session")

    chunks = list(
        stream_chat_with_memory(
            message="Remember that I know Java.",
            session_id="test-session",
            resume_text="Built APIs with Python and improved performance by 30%.",
            target_role="Backend Developer",
        )
    )

    assert len(chunks) > 1
    assert "test-session" in "".join(chunks)
    assert len(get_history("test-session")) == 2
