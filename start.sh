#!/bin/bash

# Check if running in Google Cloud environment
if [ -n "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "Attempting to fetch OpenAI API key from Google Secret Manager..."
    
    # Try to fetch the secret, with error handling
    SECRET_VALUE=$(gcloud secrets versions access latest --secret="openai-api-key" --project="${GOOGLE_CLOUD_PROJECT}" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$SECRET_VALUE" ]; then
        export OPENAI_API_KEY="$SECRET_VALUE"
        echo "Successfully retrieved OpenAI API key from Secret Manager"
    else
        echo "Warning: Failed to retrieve OpenAI API key from Secret Manager"
        echo "Falling back to environment variable OPENAI_API_KEY"
    fi
else
    echo "GOOGLE_CLOUD_PROJECT not set, using OPENAI_API_KEY environment variable"
fi

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY is not set. Please either:"
    echo "1. Set GOOGLE_CLOUD_PROJECT and ensure Secret Manager access, or"
    echo "2. Set OPENAI_API_KEY environment variable directly"
    exit 1
fi

echo "Starting application..."
# Start the application
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
