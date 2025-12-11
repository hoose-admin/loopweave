output "bigquery_dataset_id" {
  description = "BigQuery Dataset ID"
  value       = google_bigquery_dataset.loopweave.dataset_id
}

output "api_service_url" {
  description = "API Cloud Run Service URL"
  value       = google_cloud_run_service.api.status[0].url
}

output "analytics_service_url" {
  description = "Analytics Cloud Run Service URL"
  value       = google_cloud_run_service.analytics.status[0].url
}

output "frontend_service_url" {
  description = "Frontend Cloud Run Service URL"
  value       = google_cloud_run_service.frontend.status[0].url
}

output "artifact_registry_repository" {
  description = "Artifact Registry Repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.loopweave.repository_id}"
}

