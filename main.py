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
    
    # Debug: Log the raw project ID value (temporarily for debugging)
    logger.info(f"Raw GCP_PROJECT_ID value: '{project_id}' (length: {len(project_id) if project_id else 0})")
    
    if not project_id:
        logger.error("GCP_PROJECT_ID environment variable is not set")
        raise ValueError("GCP_PROJECT_ID environment variable is required")
    
    # Clean the project ID (remove any whitespace)
    project_id = project_id.strip()
    
    if not project_id:
        logger.error("GCP_PROJECT_ID is empty after stripping whitespace")
        raise ValueError("GCP_PROJECT_ID cannot be empty")
    
    # Log the cleaned project ID for debugging
    logger.info(f"Cleaned project ID: '{project_id}'")
    
    # More comprehensive project ID validation
    if len(project_id) < 6 or len(project_id) > 30:
        logger.error(f"Invalid project ID length: {len(project_id)} (must be 6-30 characters)")
        raise ValueError(f"Invalid GCP project ID length: {len(project_id)}")
    
    if not project_id[0].islower() or not project_id[-1].isalnum():
        logger.error(f"Invalid project ID format: must start with lowercase letter and end with alphanumeric")
        raise ValueError(f"Invalid GCP project ID format: {project_id}")
    
    # Check for valid characters (lowercase letters, digits, hyphens)
    import re
    if not re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$', project_id):
        logger.error(f"Invalid project ID characters: {project_id}")
        raise ValueError(f"Invalid GCP project ID format: {project_id}")
    
    try:
        # Test GCP connection first
        client = secretmanager.SecretManagerServiceClient()
        logger.info(f"Successfully created Secret Manager client")
        
        # Try to list secrets first to validate project access
        parent = f"projects/{project_id}"
        logger.info(f"Testing project access with parent: {parent}")
        
        # This will fail if the project doesn't exist or we don't have access
        try:
            # Just try to list secrets (limit to 1 to minimize cost)
            list_request = {"parent": parent, "page_size": 1}
            secrets_list = client.list_secrets(request=list_request)
            logger.info(f"Successfully accessed project: {project_id}")
        except Exception as list_error:
            logger.error(f"Failed to access project '{project_id}': {str(list_error)}")
            raise ValueError(f"Cannot access GCP project '{project_id}': {str(list_error)}")
        
        # Now try to get the specific secret
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        logger.info(f"Fetching secret: {secret_id} from project: {project_id}")
        
        response = client.access_secret_version(request={"name": name})
        logger.info(f"Successfully retrieved secret: {secret_id}")
        return response.payload.data.decode("UTF-8")
        
    except Exception as e:
        logger.error(f"Failed to access secret '{secret_id}' from project '{project_id}': {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        raise

# Get OpenAI API key from Secret Manager
try:
    logger.info("Attempting to fetch OpenAI API key from Google Cloud Secret Manager")
    # Also log environment variables for debugging
    gcp_project = os.getenv("GCP_PROJECT_ID")
    logger.info(f"GCP_PROJECT_ID from environment: '{gcp_project}'")
    
    openai_api_key = get_secret("openai-api-key")
    logger.info("Successfully retrieved OpenAI API key from Secret Manager")
except Exception as e:
    logger.error(f"Failed to fetch OpenAI API key from Secret Manager: {e}")
    logger.info("Falling back to environment variable for local development")
    # Fallback to environment variable for local development
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OpenAI API key not found in Secret Manager or environment variables")
        raise ValueError("OpenAI API key not found in Secret Manager or environment variables")
    else:
        logger.info("Using OpenAI API key from environment variable")


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