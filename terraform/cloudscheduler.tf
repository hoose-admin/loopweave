# Cloud Scheduler Job - Sync Data (3AM EST)
resource "google_cloud_scheduler_job" "sync_data" {
  name             = "sync-data"
  description      = "Sync financial data from FMP API to BigQuery"
  schedule         = "0 3 * * *"
  time_zone        = "America/New_York"
  region           = var.region
  attempt_deadline = "600s"

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_service.analytics.status[0].url}/sync"

    oidc_token {
      service_account_email = google_service_account.scheduler_invoker.email
    }
  }
}

# Cloud Scheduler Job - Calculate TA Metrics (4AM EST)
resource "google_cloud_scheduler_job" "calculate_ta_metrics" {
  name             = "calculate-ta-metrics"
  description      = "Calculate technical analysis metrics and patterns"
  schedule         = "0 4 * * *"
  time_zone        = "America/New_York"
  region           = var.region
  attempt_deadline = "1800s"

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_service.analytics.status[0].url}/ta-metrics"

    oidc_token {
      service_account_email = google_service_account.scheduler_invoker.email
    }
  }
}

