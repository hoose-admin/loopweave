output "bigquery_dataset_id" {
  description = "BigQuery Dataset ID"
  value       = google_bigquery_dataset.loopweave.dataset_id
}

output "api_service_url" {
  description = "API Cloud Run Service URL"
  value       = try(google_cloud_run_service.api.status[0].url, "Service not created yet")
}

output "analytics_service_url" {
  description = "Analytics Cloud Run Service URL"
  value       = try(google_cloud_run_service.analytics.status[0].url, "Service not created yet")
}

output "frontend_service_url" {
  description = "Frontend Cloud Run Service URL"
  value       = try(google_cloud_run_service.frontend.status[0].url, "Service not created yet")
}

output "artifact_registry_repository" {
  description = "Artifact Registry Repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.loopweave.repository_id}"
}

# Cloud SQL Outputs
output "cloudsql_instance_connection_name" {
  description = "Cloud SQL instance connection name (for Cloud SQL Proxy)"
  value       = google_sql_database_instance.loopweave_db.connection_name
}

output "cloudsql_instance_name" {
  description = "Cloud SQL instance name"
  value       = google_sql_database_instance.loopweave_db.name
}

output "cloudsql_database_name" {
  description = "Cloud SQL database name"
  value       = google_sql_database.loopweave.name
}

output "cloudsql_instance_ip_address" {
  description = "Cloud SQL instance public IP address"
  value       = google_sql_database_instance.loopweave_db.public_ip_address
}

