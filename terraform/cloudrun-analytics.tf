# Cloud Run Service - Analytics
resource "google_cloud_run_service" "analytics" {
  name     = "loopweave-analytics"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.loopweave.repository_id}/loopweave-analytics:latest"
        
        resources {
          limits = {
            cpu    = "2000m"
            memory = "2Gi"
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
          name  = "FMP_API_KEY"
          value = var.fmp_api_key
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Service account for Cloud Scheduler to invoke Analytics service
resource "google_service_account" "scheduler_invoker" {
  account_id   = "loopweave-scheduler-invoker"
  display_name = "LoopWeave Cloud Scheduler Invoker"
}

# Grant Cloud Scheduler service account permission to invoke Analytics service
resource "google_cloud_run_service_iam_member" "analytics_scheduler" {
  service  = google_cloud_run_service.analytics.name
  location = google_cloud_run_service.analytics.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler_invoker.email}"
}

