# Remember to create a GCS bucket for the backend & step 4 in terraform-setup.yml. Remove any stale Terraform lock & state
terraform {
  backend "gcs" {
    bucket = "terraform-tellsagaai"   # create this once
    prefix = "prod"                   # optional sub-folder
  }
}
