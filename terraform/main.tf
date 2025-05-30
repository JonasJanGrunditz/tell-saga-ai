resource "google_project_service" "services" {
  for_each = toset([
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "containerregistry.googleapis.com"     # or artifactregistry.googleapis.com
  ])
  project = var.project_id
  service = each.key
}



resource "google_cloud_run_service" "service" {
  name     = trim(var.cloudrun_name, " ")
  location = trim(var.region, " ")

  template {
    spec {
      containers {
        image = "gcr.io/${trim(var.project_id, " ")}/${trim(var.cloudrun_name, " ")}:latest"
        resources {
          limits = {
            cpu    = var.cpu
            memory = "1024Mi"
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  autogenerate_revision_name = true
}

resource "google_cloud_run_service_iam_member" "invoker" {
  location = google_cloud_run_service.service.location
  service  = google_cloud_run_service.service.name
  role     = "roles/run.invoker"
  member   = "allUsers"                       # or "user:alice@example.com"
}
