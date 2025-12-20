#!/bin/bash
# Helper script to load .env file and generate terraform.tfvars
# Usage: ./terraform/load-env.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"
TFVARS_FILE="$SCRIPT_DIR/terraform.tfvars"

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found at $ENV_FILE"
    echo "Please create it with your configuration"
    exit 1
fi

# Source .env file
set -a
source "$ENV_FILE"
set +a

# Generate terraform.tfvars from .env
cat > "$TFVARS_FILE" <<EOF
# Auto-generated from .env file - DO NOT EDIT MANUALLY
# Edit .env file instead and regenerate with: ./terraform/load-env.sh

project_id = "${GCP_PROJECT_ID}"
region     = "${GCP_REGION:-us-central1}"

bigquery_dataset_id = "${BIGQUERY_DATASET:-loopweave}"
bigquery_location   = "US"

fmp_api_key = "${FMP_API_KEY}"

allowed_origins = [
  "https://loopweave.io",
  "https://www.loopweave.io"
]

backend_url = "${BACKEND_URL:-}"

firebase_api_key            = "${NEXT_PUBLIC_FIREBASE_API_KEY:-}"
firebase_auth_domain        = "${NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN:-}"
firebase_project_id         = "${NEXT_PUBLIC_FIREBASE_PROJECT_ID:-}"
firebase_storage_bucket     = "${NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET:-}"
firebase_messaging_sender_id = "${NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID:-}"
firebase_app_id             = "${NEXT_PUBLIC_FIREBASE_APP_ID:-}"

stripe_publishable_key = "${NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY:-}"

# Cloud SQL
cloudsql_password = "${CLOUDSQL_PASSWORD:-}"
EOF

echo "Generated terraform.tfvars from .env file"
echo "Location: $TFVARS_FILE"

