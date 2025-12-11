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

variable "stripe_publishable_key" {
  description = "Stripe Publishable Key"
  type        = string
  sensitive   = true
  default     = ""
}

