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
from google.cloud import secretmanager
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

def get_secret(secret_id: str, project_id: str = None) -> str:
    """Fetch secret from Google Cloud Secret Manager."""
    if project_id is None:
        project_id = os.getenv("GCP_PROJECT_ID")
    
    if not project_id:
        raise ValueError("GCP_PROJECT_ID environment variable is required")
    
    project_id = project_id.strip()
    
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/663029010689/secrets/openai-api-key/versions/1"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.error(f"Failed to retrieve secret '{secret_id}' from project '{project_id}': {e}")
        raise

def get_openai_api_key() -> str:
    """Get OpenAI API key from Secret Manager or environment variable."""
    # Try Secret Manager first
    try:
        logger.info("Fetching OpenAI API key from Secret Manager")
        return get_secret("openai-api-key").strip()
    except Exception as e:
        logger.warning(f"Secret Manager failed: {e}")
        
    # Fallback to environment variable
    logger.info("Falling back to environment variable")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found in Secret Manager or OPENAI_API_KEY environment variable")
    
    return api_key.strip()

# Get OpenAI API key
try:
    openai_api_key = get_openai_api_key()
    logger.info("Successfully retrieved OpenAI API key")
except Exception as e:
    logger.error(f"Failed to get OpenAI API key: {e}")
    raise


openai_api_key = openai_api_key.strip() if openai_api_key else None
client = OpenAI(api_key=openai_api_key)

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