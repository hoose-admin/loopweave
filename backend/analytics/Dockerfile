FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for pandas
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first for better caching
COPY pyproject.toml ./

# Install dependencies using UV (extract from pyproject.toml and install)
RUN uv pip install --system --no-cache \
    fastapi==0.104.1 \
    "uvicorn[standard]==0.24.0" \
    google-cloud-bigquery==3.13.0 \
    pandas==2.1.3 \
    pandas-ta==0.3.14b0 \
    httpx==0.25.2 \
    python-dotenv==1.0.0 \
    pydantic==2.5.0

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

