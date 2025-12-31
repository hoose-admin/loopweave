# Cloud SQL PostgreSQL Instance
resource "google_sql_database_instance" "loopweave_db" {
  name             = var.cloudsql_instance_name
  database_version = "POSTGRES_15"
  region           = coalesce(var.cloudsql_region, var.region)

  # Wait for API to be fully enabled and propagated
  depends_on = [
    google_project_service.sqladmin,
    google_project_service.cloudresourcemanager
  ]
  
  # Increase timeout for instance creation (can take 5-10 minutes)
  timeouts {
    create = "15m"
    update = "15m"
    delete = "15m"
  }

  # Ignore changes to prevent update conflicts with existing instance
  # The instance was created outside Terraform, so we ignore settings that might differ
  lifecycle {
    ignore_changes = [
      deletion_protection,
      settings[0].deletion_protection_enabled,
      settings[0].tier,
      settings[0].disk_type,
      settings[0].disk_size,
      settings[0].backup_configuration,
      settings[0].ip_configuration,
      settings[0].database_flags
    ]
  }

  settings {
    tier                        = var.cloudsql_tier
    disk_type                   = var.cloudsql_disk_type
    disk_size                   = var.cloudsql_disk_size_gb
    disk_autoresize             = true
    deletion_protection_enabled = var.cloudsql_deletion_protection

    backup_configuration {
      enabled                        = var.cloudsql_backup_enabled
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = var.cloudsql_backup_retention_days
    }

    # Enable private IP for Cloud SQL Proxy via Unix socket
    # Public IP may also be enabled for direct access if needed
    ip_configuration {
      ipv4_enabled    = true  # Allow public IP (can be restricted via authorized networks)
      private_network = null  # Private IP via VPC connector if needed later
    }

    database_flags {
      name  = "max_connections"
      value = "100"
    }
  }

  deletion_protection = var.cloudsql_deletion_protection
}

# Cloud SQL Database
resource "google_sql_database" "loopweave" {
  name     = var.cloudsql_database_name
  instance = google_sql_database_instance.loopweave_db.name
  
  # Ensure instance is running before creating database
  depends_on = [
    google_sql_database_instance.loopweave_db
  ]
}

# Cloud SQL User (password from variable - store in tfvars, not in git)
resource "google_sql_user" "loopweave_app" {
  name     = var.cloudsql_user
  instance = google_sql_database_instance.loopweave_db.name
  password = var.cloudsql_password
  
  # Ensure instance and database are ready before creating user
  depends_on = [
    google_sql_database_instance.loopweave_db,
    google_sql_database.loopweave
  ]
}
