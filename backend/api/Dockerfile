FROM python:3.12-slim

WORKDIR /app

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first for better caching
COPY pyproject.toml ./

# Install dependencies using UV (extract from pyproject.toml and install)
RUN uv pip install --system --no-cache \
    fastapi==0.104.1 \
    "uvicorn[standard]==0.24.0" \
    google-cloud-bigquery==3.13.0 \
    google-cloud-firestore==2.13.0 \
    pydantic==2.5.0 \
    python-dotenv==1.0.0 \
    httpx==0.25.2

# Copy application code
COPY . .

# Expose port (Cloud Run uses PORT env var, default to 8080)
EXPOSE 8080

# Run the application (PORT env var is set by Cloud Run)
# Use sh to read PORT with fallback to 8080
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"

