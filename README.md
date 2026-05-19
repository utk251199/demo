# Simple AI Resume Reviewer API

This is a small FastAPI demo for learning how to connect an API to an AI model, stream responses into a browser, and keep short-term memory.

The important files are:

- `app/main.py` - two API routes
- `app/frontend.py` - tiny frontend page
- `app/reviewer.py` - Gemini model call and streaming logic
- `app/schemas.py` - request and response shapes
- `app/memory.py` - simple in-memory chat history

## Install

```powershell
pip install -r requirements.txt pytest
```

## Configure AI

Create a `.env` file:

```text
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

If you do not add an API key, the app returns a simple demo response instead.

## Run

```powershell
python -m uvicorn app.main:app --reload
```

Open the frontend:

```text
http://127.0.0.1:8000/
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

## Streaming Chat Endpoint

The frontend calls this endpoint and reads chunks as they arrive:

```text
POST /chat
```

The same endpoint handles resume review, follow-up chat, streaming, and memory reset.
Memory is stored in a Python dictionary while the server is running. Restarting the server clears it.

## How It Works

1. The browser loads `/`.
2. The user sends a message to `/chat`.
3. FastAPI validates the JSON body using `ChatRequest`.
4. `stream_chat_with_memory()` stores the user message by `session_id`.
5. If `GEMINI_API_KEY` exists, it streams from Gemini.
6. FastAPI sends chunks to the browser with `StreamingResponse`.
7. The browser reads chunks with `fetch()` and appends them to the page.
