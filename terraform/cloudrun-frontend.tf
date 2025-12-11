# Cloud Run Service - Frontend
resource "google_cloud_run_service" "frontend" {
  name     = "loopweave-frontend"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.loopweave.repository_id}/loopweave-frontend:latest"
        
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }

        ports {
          container_port = 3000
        }

        env {
          name  = "NEXT_PUBLIC_BACKEND_URL"
          value = var.backend_url != "" ? var.backend_url : try(google_cloud_run_service.api.status[0].url, "")
        }
        env {
          name  = "NEXT_PUBLIC_FIREBASE_API_KEY"
          value = var.firebase_api_key
        }
        env {
          name  = "NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN"
          value = var.firebase_auth_domain
        }
        env {
          name  = "NEXT_PUBLIC_FIREBASE_PROJECT_ID"
          value = var.firebase_project_id != "" ? var.firebase_project_id : var.project_id
        }
        env {
          name  = "NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET"
          value = var.firebase_storage_bucket
        }
        env {
          name  = "NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID"
          value = var.firebase_messaging_sender_id
        }
        env {
          name  = "NEXT_PUBLIC_FIREBASE_APP_ID"
          value = var.firebase_app_id
        }
        env {
          name  = "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY"
          value = var.stripe_publishable_key
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allow unauthenticated access to Frontend
resource "google_cloud_run_service_iam_member" "frontend_public" {
  service  = google_cloud_run_service.frontend.name
  location = google_cloud_run_service.frontend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

