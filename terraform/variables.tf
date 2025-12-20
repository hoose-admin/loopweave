variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "bigquery_dataset_id" {
  description = "BigQuery Dataset ID"
  type        = string
  default     = "loopweave"
}

variable "bigquery_location" {
  description = "BigQuery Dataset Location"
  type        = string
  default     = "US"
}

variable "fmp_api_key" {
  description = "Financial Modeling Prep API Key"
  type        = string
  sensitive   = true
}

variable "allowed_origins" {
  description = "Allowed CORS origins for API"
  type        = list(string)
  default     = ["https://loopweave.io", "https://www.loopweave.io"]
}

variable "backend_url" {
  description = "Backend API URL for frontend"
  type        = string
  default     = ""
}

variable "firebase_api_key" {
  description = "Firebase API Key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "firebase_auth_domain" {
  description = "Firebase Auth Domain"
  type        = string
  default     = ""
}

variable "firebase_project_id" {
  description = "Firebase Project ID"
  type        = string
  default     = ""
}

variable "firebase_storage_bucket" {
  description = "Firebase Storage Bucket"
  type        = string
  default     = ""
}

variable "firebase_messaging_sender_id" {
  description = "Firebase Messaging Sender ID"
  type        = string
  default     = ""
}

variable "firebase_app_id" {
  description = "Firebase App ID"
  type        = string
  default     = ""
}

# Cloud SQL Variables
variable "cloudsql_instance_name" {
  description = "Cloud SQL instance name"
  type        = string
  default     = "loopweave-db"
}

variable "cloudsql_database_name" {
  description = "Cloud SQL database name"
  type        = string
  default     = "loopweave"
}

variable "cloudsql_region" {
  description = "Cloud SQL region (defaults to region variable)"
  type        = string
  default     = null
}

variable "cloudsql_tier" {
  description = "Cloud SQL machine tier"
  type        = string
  default     = "db-g1-small"
}

variable "cloudsql_disk_size_gb" {
  description = "Cloud SQL disk size in GB"
  type        = number
  default     = 10
}

variable "cloudsql_disk_type" {
  description = "Cloud SQL disk type (PD_HDD or PD_SSD)"
  type        = string
  default     = "PD_HDD"
}

variable "cloudsql_backup_enabled" {
  description = "Enable Cloud SQL backups"
  type        = bool
  default     = true
}

variable "cloudsql_backup_retention_days" {
  description = "Cloud SQL backup retention days"
  type        = number
  default     = 7
}

variable "cloudsql_deletion_protection" {
  description = "Enable deletion protection for Cloud SQL instance"
  type        = bool
  default     = false
}

variable "cloudsql_user" {
  description = "Cloud SQL application user name"
  type        = string
  default     = "loopweave_app"
  sensitive   = false
}

variable "cloudsql_password" {
  description = "Cloud SQL application user password (store in tfvars, not in git)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "stripe_publishable_key" {
  description = "Stripe Publishable Key"
  type        = string
  sensitive   = true
  default     = ""
}

