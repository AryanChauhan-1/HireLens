from fastapi import FastAPI, HTTPException
from app.core import config
from google import genai

app = FastAPI(title="AlphaVerify - Week 1 Base Suite", version="1.0")
settings = config.settings

@app.get("/")
def read_root():
    return {"status": "online", "message": "AlphaVerify Week 1 Backend Server is Live"}

@app.get("/test-ai")
def test_gemini_connection():
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='Respond with exactly two words: Connection Successful.',
        )
        
        return {
            "backend_status": "FastAPI Framework Active",
            "gemini_api_status": "Connected Successfully via Gemini 2.5 Flash",
            "api_response": response.text.strip()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API Connection Failed: {str(e)}")