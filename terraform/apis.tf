# Enable required Google Cloud APIs

# Cloud Resource Manager API (required for project data source)
resource "google_project_service" "cloudresourcemanager" {
  project = var.project_id
  service = "cloudresourcemanager.googleapis.com"

  disable_on_destroy = false
}

# Secret Manager API (required for Cloud SQL password storage)
resource "google_project_service" "secretmanager" {
  project = var.project_id
  service = "secretmanager.googleapis.com"

  disable_on_destroy = false
}

# Cloud SQL Admin API (required for Cloud SQL instance creation)
resource "google_project_service" "sqladmin" {
  project = var.project_id
  service = "sqladmin.googleapis.com"

  disable_on_destroy = false
}
