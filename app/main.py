from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse

from app.frontend import FrontendPage
from app.memory import clear_history
from app.reviewer import stream_chat_with_memory
from app.schemas import ChatRequest


load_dotenv()

app = FastAPI(title="Simple AI Resume Coach")
frontend = FrontendPage()


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return frontend.render()


@app.post("/chat")
def chat(request: ChatRequest) -> StreamingResponse:
    if request.reset_memory:
        clear_history(request.session_id)
        return StreamingResponse(iter(["Memory cleared."]), media_type="text/plain")

    return StreamingResponse(
        stream_chat_with_memory(
            message=request.message,
            session_id=request.session_id,
            resume_text=request.resume_text,
            target_role=request.target_role,
        ),
        media_type="text/plain",
    )
