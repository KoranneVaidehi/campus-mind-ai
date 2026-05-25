"""
FastAPI Server for Multilingual Academic Assistant
Integrates with existing AcademicAssistant class
"""
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn

# Add parent directory to path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from main import AcademicAssistant
from translation.translation_wrapper import TranslationWrapper

# Initialize FastAPI
app = FastAPI(title="Nexus AI - Multilingual Academic Assistant")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot (lazy loading)
chatbot = None
translator = None

def get_chatbot():
    global chatbot, translator
    if chatbot is None:
        print("🚀 Initializing Academic Assistant...")
        chatbot = AcademicAssistant()
        chatbot.setup()
        translator = TranslationWrapper(chatbot)
        print("✅ Chatbot ready!")
    return chatbot, translator

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    detected_language: str
    sources: List[str]
    is_pdf_request: bool = False
    pdf_path: Optional[str] = None
    pdf_name: Optional[str] = None

class PDFUploadResponse(BaseModel):
    success: bool
    message: str
    filename: Optional[str] = None

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Nexus AI API is running", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "chatbot_ready": chatbot is not None}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the chatbot"""
    try:
        bot, trans = get_chatbot()
        
        # Process through translation wrapper
        result = trans.process_query(request.message)
        
        return ChatResponse(
            response=result['response_translated'],
            detected_language=result['detected_language'],
            sources=result.get('sources', []),
            is_pdf_request=result.get('is_pdf_request', False),
            pdf_path=result.get('pdf_result', {}).get('pdf_path'),
            pdf_name=result.get('pdf_result', {}).get('pdf_name')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "hi", "name": "Hindi"},
            {"code": "mr", "name": "Marathi"},
            {"code": "gu", "name": "Gujarati"},
            {"code": "ta", "name": "Tamil"},
            {"code": "te", "name": "Telugu"}
        ]
    }

@app.get("/pdfs")
async def get_available_pdfs():
    """Get list of available PDFs"""
    bot, _ = get_chatbot()
    return {"pdfs": list(bot.available_pdfs.keys())}

# Run server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)