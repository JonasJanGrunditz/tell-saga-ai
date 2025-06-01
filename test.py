from google.cloud import secretmanager
client = secretmanager.SecretManagerServiceClient()
def access_secret(project_id, secret_id, version_id=1):
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
PROJECT_ID = "mittliv"
SECRET_ID = "openai-api-key"
secret_value = access_secret(
  project_id=PROJECT_ID, 
  secret_id=SECRET_ID
)
print("Secret value:", secret_value)