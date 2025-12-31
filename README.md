Pro Tip for "Querying by Symbol"
Regardless of the engine you choose, you should use Table Partitioning and Clustering (Indexes) to keep your queries fast as the database grows:
1 Partition by Date: Divide your table into monthly or yearly chunks.
2 Index by Symbol: Create a B-Tree index (or a Composite Index on symbol + date). This ensures that when you query WHERE symbol = 'AAPL', the database skips millions of irrelevant rows and goes straight to the Apple data.

# LoopWeave

A minimalist stock trading metrics visualization platform.

## Architecture

- **Frontend**: Next.js with TypeScript, styled-components, Plotly.js
- **Backend API**: FastAPI on Cloud Run
- **Analytics Service**: FastAPI on Cloud Run (for data processing)
- **Data Storage**: BigQuery (timeseries, stocks, patterns)
- **Authentication**: Firebase Authentication
- **User Data**: Firestore
- **Payments**: Stripe

## Setup

### Prerequisites

- Node.js 18+
- Python 3.11+
- UV (Python package manager) - Install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Make (usually pre-installed on macOS/Linux)
- Google Cloud SDK
- Docker

### Quick Start

The easiest way to get started is using the Makefile:

```bash
# Setup and start all services
make start

# Or manually:
make setup-all    # Install dependencies and setup .env files
make dev-all      # Start all services
```

### Individual Service Setup

#### Using Makefile (Recommended)

```bash
# Frontend
make setup-frontend
make dev-frontend

# API Backend
make setup-api
make dev-api

# Analytics Backend
make setup-analytics
make dev-analytics
```

#### Manual Setup

**Frontend:**

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your configuration
npm run dev
```

**Backend API:**

```bash
cd backend/api
uv sync
cp .env.example .env
# Edit .env with your configuration
uv run uvicorn main:app --reload
```

**Analytics Service:**

```bash
cd backend/analytics
uv sync
cp .env.example .env
# Edit .env with your configuration
uv run uvicorn main:app --reload --port 8001
```

### Makefile Commands

Run `make help` to see all available commands:

- `make setup-all` - Install dependencies and setup .env files for all services
- `make dev-all` - Start all services (frontend + both backends)
- `make dev-frontend` - Start only frontend
- `make dev-api` - Start only API backend
- `make dev-analytics` - Start only Analytics backend
- `make clean-all` - Clean all build artifacts
- `make stop` - Stop all running services

### BigQuery Setup

```bash
chmod +x scripts/setup-bigquery.sh
./scripts/setup-bigquery.sh
```

### Seed Historical Stock Data

To seed BigQuery with historical stock data for testing:

```bash
# First, ensure scripts dependencies are installed
cd scripts && uv sync

# Using the script directly
cd scripts && uv run seed-stock-data.py AAPL

# Or using Makefile (recommended)
make seed-stock SYMBOL=AAPL

# Check existing data without fetching
cd scripts && uv run seed-stock-data.py AAPL --check-only
```

**Note**:

- Environment variables are loaded from the root `.env` file
- Make sure you have set `FMP_API_KEY`, `GCP_PROJECT_ID`, and `BIGQUERY_DATASET` in the root `.env` file
- Ensure your Google Cloud credentials are configured

### Deployment

**Infrastructure is managed with Terraform:**

1. **Setup Terraform:**

   ```bash
   # Generate terraform.tfvars from .env file
   make terraform-load-env

   # Initialize Terraform
   make terraform-init
   ```

2. **Deploy Infrastructure:**

   ```bash
   # Plan changes
   make terraform-plan

   # Apply changes (creates all infrastructure)
   make terraform-apply
   ```

3. **Build and Push Docker Images:**

   ```bash
   # Build and push all images
   make build-push-all

   # Or individually:
   make build-push-api
   make build-push-analytics
   make build-push-frontend
   ```

**What Terraform Creates:**

- BigQuery dataset and tables (timeseries, stocks, patterns, trades)
- Artifact Registry repository
- Cloud Run services (API, Analytics, Frontend)
- Cloud Scheduler jobs (sync at 3AM EST, ta-metrics at 4AM EST)
- IAM roles and service accounts

**Terraform Commands:**

- `make terraform-load-env` - Generate terraform.tfvars from .env
- `make terraform-init` - Initialize Terraform
- `make terraform-plan` - Preview changes
- `make terraform-apply` - Apply changes
- `make terraform-destroy` - Destroy infrastructure
- `make terraform-output` - Show outputs (service URLs, etc.)

See `terraform/README.md` for detailed Terraform documentation.

## Project Structure

```
loopweave/
├── frontend/          # Next.js frontend application
├── backend/
│   ├── api/          # FastAPI API service
│   └── analytics/    # FastAPI analytics service
├── scripts/          # Deployment and setup scripts
└── plan.md          # Project plan (DO NOT EDIT)
```

## Environment Variables

See `.env.example` files in each directory for required environment variables.

## Development

The frontend runs on `http://localhost:3000` and the backend API on `http://localhost:8000` by default.

## License

Private
