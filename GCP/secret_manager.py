from google.cloud import secretmanager
import requests
import os

def get_project_id():
    """Get the current GCP project ID from metadata service."""
    try:
        # When running on GCP (Cloud Run, Compute Engine, etc.)
        response = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id",
            headers={"Metadata-Flavor": "Google"},
            timeout=5
        )
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        pass
    
    # Fallback to environment variable or hardcoded value
    return os.getenv("GOOGLE_CLOUD_PROJECT", "mittliv")



client = secretmanager.SecretManagerServiceClient()
def access_secret(secret_id, version_id=1):
    name = f"projects/{get_project_id()}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")