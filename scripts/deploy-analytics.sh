#!/bin/bash

# Deploy Analytics Cloud Run instance
# Usage: ./scripts/deploy-analytics.sh

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
SERVICE_NAME="loopweave-analytics"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "Building Docker image..."
cd backend/analytics
docker build -t ${IMAGE_NAME} .

echo "Pushing to Artifact Registry..."
docker push ${IMAGE_NAME}

# Get FMP API key from environment or use default
FMP_API_KEY=${FMP_API_KEY:-""}

echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --no-allow-unauthenticated \
  --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID},BIGQUERY_DATASET=loopweave,FMP_API_KEY=${FMP_API_KEY}"

echo "Deployment complete!"

