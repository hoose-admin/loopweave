# Artifact Registry Repository
resource "google_artifact_registry_repository" "loopweave" {
  location      = var.region
  repository_id = "loopweave"
  description   = "Docker repository for LoopWeave services"
  format        = "DOCKER"
}

# Cloud Run Service - API
resource "google_cloud_run_service" "api" {
  name     = "loopweave-api"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.loopweave.repository_id}/loopweave-api:latest"
        
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }

        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }
        env {
          name  = "BIGQUERY_DATASET"
          value = var.bigquery_dataset_id
        }
        env {
          name  = "ALLOWED_ORIGINS"
          value = join(",", var.allowed_origins)
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allow unauthenticated access to API
resource "google_cloud_run_service_iam_member" "api_public" {
  service  = google_cloud_run_service.api.name
  location = google_cloud_run_service.api.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

