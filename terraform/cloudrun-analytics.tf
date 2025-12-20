# Cloud Run Service - Analytics
resource "google_cloud_run_service" "analytics" {
  name     = "loopweave-analytics"
  location = var.region

  template {
    metadata {
      annotations = {
        "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.loopweave_db.connection_name
      }
    }
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
        # Cloud SQL connection via Unix socket (Cloud SQL Proxy)
        env {
          name  = "CLOUDSQL_INSTANCE_CONNECTION_NAME"
          value = google_sql_database_instance.loopweave_db.connection_name
        }
        env {
          name  = "CLOUDSQL_DATABASE_NAME"
          value = var.cloudsql_database_name
        }
        env {
          name  = "CLOUDSQL_USER"
          value = var.cloudsql_user
        }
        env {
          name  = "CLOUDSQL_PASSWORD"
          value = var.cloudsql_password
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

# Get project data for service account reference
data "google_project" "project" {
  project_id = var.project_id

  depends_on = [google_project_service.cloudresourcemanager]
}

# Grant Cloud Run service account permission to connect to Cloud SQL via Unix socket
resource "google_project_iam_member" "cloudrun_cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
  
  depends_on = [
    data.google_project.project,
    google_sql_database_instance.loopweave_db
  ]
}

