#!/bin/bash

# Deploy Frontend to Cloud Run
# Usage: ./scripts/deploy-frontend.sh

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
SERVICE_NAME="loopweave-frontend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Get backend URL from environment or use default
BACKEND_URL=${BACKEND_URL:-"https://loopweave-api-xxxxx.run.app"}

echo "Building Docker image..."
cd frontend
docker build -t ${IMAGE_NAME} .

echo "Pushing to Artifact Registry..."
docker push ${IMAGE_NAME}

echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --port 3000 \
  --set-env-vars "NEXT_PUBLIC_BACKEND_URL=${BACKEND_URL},NEXT_PUBLIC_FIREBASE_API_KEY=${NEXT_PUBLIC_FIREBASE_API_KEY},NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=${NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN},NEXT_PUBLIC_FIREBASE_PROJECT_ID=${NEXT_PUBLIC_FIREBASE_PROJECT_ID},NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=${NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET},NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=${NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID},NEXT_PUBLIC_FIREBASE_APP_ID=${NEXT_PUBLIC_FIREBASE_APP_ID},NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=${NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY}"

echo "Deployment complete!"
echo "Frontend URL: https://${SERVICE_NAME}-xxxxx-${REGION}.a.run.app"

