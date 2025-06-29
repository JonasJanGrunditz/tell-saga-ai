import logging
import sys
import os
import asyncio
import json
import uvicorn
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request, status, UploadFile, File
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
from pydantic import ValidationError
from openai import AsyncOpenAI
from google.cloud import secretmanager
from LLM.model import call_openai
from GCP.secret_manager import access_secret
from LLM.voice_to_text import call_voice_to_text

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(MODULE_DIR)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logger = logging.getLogger("chatbot")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)
logger.setLevel(LOG_LEVEL)




openai_api_key = access_secret(
  secret_id="openai-api-key"
)
client = AsyncOpenAI(
    api_key=openai_api_key,
    timeout=30.0,
    max_retries=2
)

app = FastAPI(title="Customer-Service Chatbot", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat", response_model=Dict[str, Any], status_code=200)
async def chat(request: Request) -> JSONResponse:  # noqa: D401


    try:
        body: Dict[str, Any] = await request.json()
    except json.JSONDecodeError as exc:
        logger.warning("Malformed JSON received: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload."
        ) 
    
    text: Optional[str] = body.get("text")
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Text field is required."
        )

    try:
       
        response = await call_openai(text, client, functionality='chat')
        logger.info(f"Generated story for input: {text}...")
        return JSONResponse(content={"reply": response.story})
    except ValidationError as exc:
        # Handle case where OpenAI returns plain text rejection instead of structured output
        logger.warning(f"Content rejected by OpenAI safety filters: {exc}")
        return JSONResponse(content={"reply": "Jag kan inte hjälpa till att förbättra denna typ av innehåll."})
    except Exception as exc:
        logger.error(f"Error calling OpenAI: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate response."
        )
    

@app.post("/suggestions", response_model=Dict[str, Any], status_code=200)
async def suggestions(request: Request) -> JSONResponse:  # noqa: D401

    try:
        body: Dict[str, Any] = await request.json()
    except json.JSONDecodeError as exc:
        logger.warning("Malformed JSON received: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload."
        )

    text: Optional[str] = body.get("text")

    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text field is required."
        )

    try:
        response = await call_openai(text, client, functionality='suggestions')
        logger.info(f"Generated story for input: {text}...")
        return JSONResponse(content={"reply": response.suggestions})
    except ValidationError as exc:
        # Handle case where OpenAI returns plain text rejection instead of structured output
        logger.warning(f"Content rejected by OpenAI safety filters: {exc}")
        return JSONResponse(content={"reply": ["Jag kan inte ge förslag på denna typ av innehåll.","Jag kan inte ge förslag på denna typ av innehåll.","Jag kan inte ge förslag på denna typ av innehåll."]})
    except Exception as exc:
        logger.error(f"Error calling OpenAI: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate response."
        )
    


@app.post("/transcribe", response_model=Dict[str, Any], status_code=200)
async def transcribe_audio(audio_file: UploadFile = File(...)) -> JSONResponse:
    """
    Transcribe uploaded audio file to text.
    
    Args:
        audio_file: The audio file to transcribe (supports mp4, webm, wav, etc.)
        
    Returns:
        JSONResponse with transcribed text
    """
    
    # Validate file type
    allowed_types = [
        "audio/mp4", "audio/webm", "audio/wav", 
        "audio/ogg", "audio/mpeg", "audio/m4a"
    ]
    
    # Extract base MIME type (remove codec parameters)
    base_content_type = audio_file.content_type.split(';')[0] if audio_file.content_type else ""
    
    if base_content_type not in allowed_types:
        logger.warning(f"Unsupported file type: {audio_file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format. Supported formats: {', '.join(allowed_types)}"
        )
    
    # Validate file size (e.g., max 25MB)
    max_file_size = 25 * 1024 * 1024  # 25MB in bytes
    file_content = await audio_file.read()
    
    if len(file_content) > max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size too large. Maximum size is 25MB."
        )
    
    try:
        # Create a temporary file to save the uploaded audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.filename.split('.')[-1]}") as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            transcribed_text = call_voice_to_text(client, temp_file_path)
            logger.info(f"Successfully transcribed audio file: {audio_file.filename}")
            return JSONResponse(content={"transcription": transcribed_text})
            
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as exc:
        logger.error(f"Error transcribing audio: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transcribe audio file."
        )



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)