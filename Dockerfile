FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PyTorch and other libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
# This layer will only rebuild if requirements.txt changes
COPY requirements.txt .

# Install PyTorch CPU-only version first (much smaller and faster than full PyTorch)
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu \
    torch==2.1.0+cpu \
    torchvision==0.16.0+cpu

# Install remaining Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy English models for Presidio (after pip install)
# en_core_web_sm: Lightweight model for Presidio (faster, smaller)
# en_core_web_lg: Large model for better accuracy (already used)
RUN python -m spacy download en_core_web_sm && \
    python -m spacy download en_core_web_lg

# Create non-root user for Celery worker (UID 1000 matches common host user)
# Note: User creation may fail if already exists, which is acceptable
RUN (useradd -m -u 1000 -s /bin/bash celeryuser 2>/dev/null || true) && \
    chown -R celeryuser:celeryuser /app 2>/dev/null || true

# Copy all application code last (after dependencies are installed)
# This layer will rebuild on code changes, but dependencies are cached
COPY . .

# Ensure app directory is accessible
RUN chmod -R 755 /app

# Expose port (8000 for local, 8080 for Google Cloud Run)
EXPOSE 8000
EXPOSE 8080

# Default command (can be overridden in docker-compose or Cloud Run)
# Google Cloud Run uses PORT environment variable, defaults to 8080
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]


