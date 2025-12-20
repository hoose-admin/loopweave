FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for pandas
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first for better caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Cloud Run uses PORT env var, default to 8080)
EXPOSE 8080

# Run the application (PORT env var is set by Cloud Run)
# Use sh to read PORT with fallback to 8080
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"

