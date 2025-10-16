from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI(title="Healthcare Symptom Chat – Gemini 2.5 Pro")

# Serve static & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ✅ Direct Gemini API key (replace with your own)
GEMINI_API_KEY = "AIzaSyDvVr8iajZWz2iTydxXZsM2rg6v31OB7aE"

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(request: Request):
    """Handle multi-turn chat with Gemini 2.5 Pro"""
    data = await request.json()
    messages = data.get("messages", [])

    # Build Gemini input format
    formatted_messages = [
        {
            "role": "user" if m["sender"] == "user" else "model",
            "parts": [{"text": m["text"]}]
        }
        for m in messages
    ]

    payload = {"contents": formatted_messages}

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    try:
        # ✅ Use Gemini 2.5 Pro endpoint
        r = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent",
            headers=headers,
            json=payload
        )
        r.raise_for_status()
        result = r.json()

        reply = result["candidates"][0]["content"]["parts"][0]["text"]
        return JSONResponse({"reply": reply})

    except Exception as e:
        return JSONResponse({"reply": f"❌ Error: {e}"})
