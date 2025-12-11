# LoopWeave Infrastructure as Code

This directory contains Terraform configurations for deploying all LoopWeave infrastructure to Google Cloud Platform.

## Prerequisites

1. Install Terraform: https://www.terraform.io/downloads
2. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install
3. **Set up authentication:**

   ```bash
   # Option 1: Use Application Default Credentials (recommended)
   # First, ensure you're using the correct account:
   gcloud config set account YOUR_ACCOUNT_EMAIL
   gcloud config set project loopweave

   # Then authenticate for application default credentials:
   gcloud auth application-default login

   # Option 2: Use a service account key file
   # Set the environment variable:
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
   ```

4. **Enable required APIs manually** (required due to organization-level permissions):
   ```bash
   gcloud services enable serviceusage.googleapis.com --project=YOUR_PROJECT_ID
   gcloud services enable cloudbuild.googleapis.com --project=YOUR_PROJECT_ID
   gcloud services enable run.googleapis.com --project=YOUR_PROJECT_ID
   gcloud services enable cloudscheduler.googleapis.com --project=YOUR_PROJECT_ID
   gcloud services enable artifactregistry.googleapis.com --project=YOUR_PROJECT_ID
   gcloud services enable bigquery.googleapis.com --project=YOUR_PROJECT_ID
   gcloud services enable iam.googleapis.com --project=YOUR_PROJECT_ID
   ```

## Setup

1. Copy the example variables file:

   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. Edit `terraform.tfvars` with your values:

   - `project_id`: Your GCP Project ID
   - `fmp_api_key`: Your Financial Modeling Prep API key
   - Firebase configuration variables
   - Stripe publishable key

3. Initialize Terraform:
   ```bash
   cd terraform
   terraform init
   ```

## Usage

### Plan Changes

```bash
terraform plan
```

### Apply Changes

```bash
terraform apply
```

### Destroy Infrastructure

```bash
terraform destroy
```

## What Gets Created

- **BigQuery**: Dataset and 4 tables (timeseries, stocks, patterns, trades)
- **Artifact Registry**: Docker repository for container images
- **Cloud Run Services**:
  - `loopweave-api` (public)
  - `loopweave-analytics` (private, invoked by scheduler)
  - `loopweave-frontend` (public)
- **Cloud Scheduler**: 2 cron jobs (sync at 3AM EST, ta-metrics at 4AM EST)
- **IAM**: Service accounts and permissions

## Building and Pushing Docker Images

Terraform creates the infrastructure, but you still need to build and push Docker images:

```bash
# Build and push API
cd backend/api
docker build -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/loopweave/loopweave-api:latest .
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/loopweave/loopweave-api:latest

# Build and push Analytics
cd backend/analytics
docker build -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/loopweave/loopweave-analytics:latest .
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/loopweave/loopweave-analytics:latest

# Build and push Frontend
cd frontend
docker build -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/loopweave/loopweave-frontend:latest .
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/loopweave/loopweave-frontend:latest
```

Or use the Makefile targets (see main README).

## Outputs

After applying, Terraform will output:

- BigQuery dataset ID
- API service URL
- Analytics service URL
- Frontend service URL
- Artifact Registry repository URL

## Variables

See `variables.tf` for all available variables and their descriptions.
