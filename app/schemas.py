from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=2)
    session_id: str = "demo"
    resume_text: str | None = None
    target_role: str | None = None
    reset_memory: bool = False
