#!/bin/bash

# Setup Cloud Scheduler jobs
# Usage: ./scripts/setup-scheduler.sh

set -e

# Try to get project from gcloud config if not set
if [ -z "$GCP_PROJECT_ID" ]; then
    GCP_PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    if [ -z "$GCP_PROJECT_ID" ]; then
        echo "Error: GCP_PROJECT_ID environment variable is not set"
        echo "Please set it in your root .env file or run:"
        echo "  gcloud config set project YOUR_PROJECT_ID"
        echo "  export GCP_PROJECT_ID=YOUR_PROJECT_ID"
        exit 1
    fi
    echo "Using GCP project from gcloud config: $GCP_PROJECT_ID"
fi

PROJECT_ID=${GCP_PROJECT_ID}
REGION=${GCP_REGION:-"us-central1"}
ANALYTICS_SERVICE_URL=${ANALYTICS_SERVICE_URL:-"https://loopweave-analytics-xxxxx.run.app"}

echo "Creating Cloud Scheduler job for /sync (3AM EST)..."
gcloud scheduler jobs create http sync-data \
  --location=${REGION} \
  --schedule="0 3 * * *" \
  --time-zone="America/New_York" \
  --uri="${ANALYTICS_SERVICE_URL}/sync" \
  --http-method=POST \
  --oidc-service-account-email=${PROJECT_ID}@appspot.gserviceaccount.com

echo "Creating Cloud Scheduler job for /ta-metrics (4AM EST)..."
gcloud scheduler jobs create http calculate-ta-metrics \
  --location=${REGION} \
  --schedule="0 4 * * *" \
  --time-zone="America/New_York" \
  --uri="${ANALYTICS_SERVICE_URL}/ta-metrics" \
  --http-method=POST \
  --oidc-service-account-email=${PROJECT_ID}@appspot.gserviceaccount.com

echo "Cloud Scheduler setup complete!"

