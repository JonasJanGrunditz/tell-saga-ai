import logging
import sys
import os
import asyncio
import json
import uvicorn
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import OpenAI
from LLM.model import call_openai


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

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
       
        response = call_openai(text, client)
        logger.info(f"Generated story for input: {text}...")
        return JSONResponse(content={"reply": response.story})
    except Exception as exc:
        logger.error(f"Error calling OpenAI: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate response."
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)