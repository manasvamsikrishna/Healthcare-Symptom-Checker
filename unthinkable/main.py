from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import time

app = FastAPI(title="Healthcare Symptom Chat – Gemini 2.5 Pro")

# Serve static & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ✅ Replace with your own API key
GEMINI_API_KEY = "AIzaSyApu41jM5ergZV4l-Ts3Hwtoaz3isFvKNA"

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(request: Request):
    """Handle multi-turn chat with Gemini 2.5 Pro + Fallback"""
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
    headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}

    # ✅ Try multiple models in order
    gemini_models = [
        "gemini-2.5-pro",
        "gemini-1.5-flash"
    ]

    for model in gemini_models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            r = requests.post(url, headers=headers, json=payload)
            
            if r.status_code == 429:  # Too Many Requests
                print(f"⚠️ Rate limit hit for {model}, trying fallback...")
                time.sleep(1)  # Avoid spamming
                continue

            r.raise_for_status()
            result = r.json()
            reply = result["candidates"][0]["content"]["parts"][0]["text"]
            return JSONResponse({"reply": reply})

        except Exception as e:
            print(f"❌ Error with {model}: {e}")
            continue

    # ✅ Final fallback response if all models fail
    return JSONResponse({"reply": "⚠️ The AI service is currently overloaded. Please try again in a few seconds."})
