# LoopWeave Architecture

## Overview

LoopWeave is a minimalist stock trading metrics visualization platform built with a modern serverless architecture on Google Cloud Platform.

## System Architecture

```
┌─────────────────┐
│   Next.js App   │ (Frontend - Cloud Run)
│   (TypeScript)  │
└────────┬─────────┘
         │
         ├─── Firebase Auth ───> Firebase Authentication
         ├─── Firestore ────────> Firestore (User Data)
         └─── API Routes ──────> ┌─────────────────┐
                                  │  FastAPI API    │ (Backend API - Cloud Run)
                                  └────────┬────────┘
                                           │
                                           └───> BigQuery
                                                  ├── timeseries
                                                  ├── stocks
                                                  └── patterns

┌─────────────────┐
│ Cloud Scheduler │
└────────┬────────┘
         │
         ├─── 3AM EST ───> ┌──────────────────┐
         │                 │ Analytics Service│ (FastAPI - Cloud Run)
         │                 └────────┬─────────┘
         │                          │
         │                          ├─── FMP API ───> Financial Modeling Prep
         │                          └─── BigQuery ───> Data Storage
         │
         └─── 4AM EST ───> Analytics Service (/ta-metrics)
```

## Components

### Frontend (Next.js)

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: styled-components (NO Tailwind)
- **Charts**: Plotly.js (custom bundle: line, scatter, bar, candlestick)
- **Icons**: Material UI Icons
- **Authentication**: Firebase Auth
- **State Management**: React hooks + Firestore

**Pages**:
- `/` - Landing page
- `/login` - Authentication
- `/account` - User profile management
- `/micro/[userUuid]` - Micro feed with metric selection
- `/micro/[userUuid]/stock/[symbol]` - Stock detail page
- `/subscribe` - Subscription page

### Backend API (FastAPI)

**Endpoints**:
- `GET /timeseries` - Get stock timeseries data
- `GET /patterns/{pattern_type}` - Get pattern data
- `GET /stocks` - List all stocks
- `GET /stocks/{symbol}` - Get specific stock

**Technology**:
- FastAPI (Python)
- Google Cloud BigQuery client
- Pydantic for type validation

### Analytics Service (FastAPI)

**Endpoints**:
- `POST /sync` - Sync data from FMP API to BigQuery
- `POST /ta-metrics` - Calculate technical analysis metrics

**Technology**:
- FastAPI (Python)
- pandas-ta for technical analysis
- Financial Modeling Prep API integration
- Google Cloud BigQuery client

### Data Storage (BigQuery)

**Tables**:

1. **timeseries**
   - Partitioned by `timestamp`
   - Clustered by `stock_symbol`
   - Contains: OHLCV data + calculated TA metrics (EMA, SMA, MACD, RSI)

2. **stocks**
   - Contains: Company profile data (symbol, name, sector, financials)

3. **patterns**
   - Clustered by `stock_symbol` and `pattern_type`
   - Contains: Candlestick patterns with timestamps

### Authentication & User Data

- **Firebase Authentication**: Username/password authentication
- **Firestore**: User profiles, favorites, subscription status

### Infrastructure

- **Cloud Run**: Hosts frontend, API, and analytics services
- **Cloud Scheduler**: Daily cron jobs for data sync and TA calculations
- **BigQuery**: Data warehouse for financial data
- **Firebase**: Authentication and user data storage

## Data Flow

### Daily Data Sync (3AM EST)

1. Cloud Scheduler triggers `/sync` endpoint
2. Analytics service fetches latest data from FMP API
3. Data is inserted into BigQuery `timeseries` table

### Daily TA Calculation (4AM EST)

1. Cloud Scheduler triggers `/ta-metrics` endpoint
2. Analytics service:
   - Fetches timeseries data from BigQuery
   - Calculates TA metrics (EMA, SMA, MACD, RSI)
   - Detects candlestick patterns
   - Updates `timeseries` table with metrics
   - Inserts patterns into `patterns` table

### User Request Flow

1. User navigates to `/micro/[userUuid]`
2. Frontend calls `/api/micro/metrics?metric={metric}`
3. Next.js API route proxies to backend API
4. Backend queries BigQuery for matching stocks
5. Results returned to frontend and displayed as cards

## Design System

### Colors
- `#FFF` - Background/primary surfaces
- `#AAA` - Secondary text/elements
- `#666` - Tertiary text
- `#333` - Primary text
- `#64a7fa` - Primary accent
- `#ff7878` - Secondary accent

### Typography
- Logo/Heading: "Asimovian"
- Body: "Poiret One"
- Details: "Roboto"

## Deployment

All services are containerized with Docker and deployed to Cloud Run:

1. **Frontend**: `scripts/deploy-frontend.sh` (to be created)
2. **API**: `scripts/deploy-api.sh`
3. **Analytics**: `scripts/deploy-analytics.sh`
4. **BigQuery**: `scripts/setup-bigquery.sh`
5. **Scheduler**: `scripts/setup-scheduler.sh`

## Environment Variables

See `.env.example` files in each directory for required configuration.

