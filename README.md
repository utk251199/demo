# Simple AI Resume Reviewer API

This is a small FastAPI demo for learning how to connect an API to an AI model.

The important files are:

- `app/main.py` - API routes
- `app/reviewer.py` - Gemini model call
- `app/schemas.py` - request and response shapes

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

Open the docs:

```text
http://127.0.0.1:8000/docs
```

## Test Request

```powershell
curl -X POST http://127.0.0.1:8000/review `
  -H "Content-Type: application/json" `
  -d "{\"resume_text\":\"Built APIs with Python and improved performance by 30%.\",\"target_role\":\"Backend Developer\"}"
```

## How It Works

1. The user sends resume text to `/review`.
2. FastAPI validates the JSON body using `ReviewRequest`.
3. `review_resume()` checks for `GEMINI_API_KEY`.
4. If the key exists, it calls the Gemini model.
5. If the key is missing, it returns a local demo review.
