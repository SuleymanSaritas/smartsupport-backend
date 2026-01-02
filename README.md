# SmartSupport Backend API

Production-ready FastAPI backend for multi-lingual customer support ticket classification system with ML-powered intent detection, PII masking, and asynchronous processing.

## Features

- **Multi-lingual Support**: Automatically detects Turkish or English and routes to appropriate AI model
- **Translation Layer**: Turkish queries are translated to English for improved accuracy using the Banking77 model
- **PII Masking**: Masks sensitive information including Turkish Identity Numbers (TCKN), emails, phone numbers, credit cards, and IP addresses using Microsoft Presidio
- **Async Processing**: Uses Celery + Redis for asynchronous ticket processing
- **Rate Limiting**: Built-in rate limiting (5 requests/minute) using slowapi
- **Natural Language Responses**: Generates humanized, varied responses in both Turkish and English
- **Top 3 Predictions**: Returns top 3 intent predictions with confidence scores
- **Dockerized**: Fully containerized with Docker Compose for easy local development
- **Production Ready**: Includes proper error handling, logging, API key authentication, and health checks

## Tech Stack

- **Framework**: FastAPI (Python 3.9+)
- **Async Processing**: Celery + Redis
- **ML Libraries**: transformers, torch (CPU-only), langdetect, deep-translator
- **PII Masking**: presidio-analyzer, presidio-anonymizer, spacy
- **Database**: SQLite (with WAL mode for concurrent access)
- **Models**:
  - English: `philschmid/BERT-Banking77` (77 banking intents)
  - Translation: Google Translator API for Turkish → English

## Prerequisites

### Local Development
- Python 3.9+
- Docker and Docker Compose
- Redis (or use Docker Compose)

### Google Cloud Deployment
- Google Cloud Platform account
- Google Cloud SDK installed
- Cloud Run API enabled
- Cloud Build API enabled
- (Optional) Cloud Memorystore for Redis

## Local Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd smartsupport-backend
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```bash
# API Configuration
API_KEY=your-secret-api-key-here-change-in-production

# Redis Configuration (defaults work for Docker Compose)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Optional: Override defaults
DEBUG=False
```

### 3. Run with Docker Compose (Recommended)

This is the easiest way to get started:

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

This will start:
- **Redis** on port 6379
- **Backend API** on port 8000
- **Celery Worker** for async processing

The API will be available at: `http://localhost:8000`

### 4. Local Development (without Docker)

If you prefer to run without Docker:

#### Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install PyTorch CPU-only (required first)
pip install --index-url https://download.pytorch.org/whl/cpu torch==2.1.0+cpu torchvision==0.16.0+cpu

# Install other dependencies
pip install -r requirements.txt

# Download spaCy models
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_lg
```

#### Start Services

**Terminal 1 - Redis:**
```bash
redis-server
```

**Terminal 2 - Backend API:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 3 - Celery Worker:**
```bash
celery -A app.worker.celery_app worker --loglevel=info --concurrency=2
```

### 5. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "models_loaded": true,
#   "translation_enabled": true
# }
```

## Google Cloud Deployment

### Prerequisites

1. **Install Google Cloud SDK**
   ```bash
   # Follow: https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate and Set Project**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Enable Required APIs**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

### Option 1: Deploy via Cloud Build (Recommended)

This uses the `cloudbuild.yaml` configuration file:

```bash
# Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml

# Monitor build progress
gcloud builds list --limit=1
```

The build will:
1. Build Docker image
2. Push to Container Registry
3. Deploy to Cloud Run with configured settings

### Option 2: Deploy via Cloud Run CLI

Direct deployment from source:

```bash
gcloud run deploy smartsupport-backend \
  --source . \
  --region europe-west3 \
  --platform managed \
  --port 8080 \
  --memory 8Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 1 \
  --no-cpu-throttling \
  --set-env-vars "API_KEY=your-api-key,PORT=8080" \
  --allow-unauthenticated
```

### Option 3: Deploy Pre-built Image

If you've already built the image:

```bash
# Build locally
docker build -t gcr.io/YOUR_PROJECT_ID/smartsupport-backend .

# Push to Container Registry
docker push gcr.io/YOUR_PROJECT_ID/smartsupport-backend

# Deploy to Cloud Run
gcloud run deploy smartsupport-backend \
  --image gcr.io/YOUR_PROJECT_ID/smartsupport-backend \
  --region europe-west3 \
  --platform managed \
  --port 8080 \
  --memory 8Gi \
  --cpu 2
```

### Environment Variables in Cloud Run

Set environment variables via Cloud Console or CLI:

```bash
gcloud run services update smartsupport-backend \
  --update-env-vars API_KEY=your-secure-api-key,REDIS_HOST=your-redis-ip
```

**Required Variables:**
- `API_KEY`: Your secret API key for authentication
- `PORT`: Set to `8080` (Cloud Run default)

**Optional Variables:**
- `REDIS_HOST`: Redis instance IP (if using Cloud Memorystore)
- `REDIS_PORT`: Redis port (default: 6379)
- `DEBUG`: Set to `False` for production

### Redis Setup (Cloud Memorystore)

For production, use Cloud Memorystore instead of in-container Redis:

1. **Create Redis Instance**
   ```bash
   gcloud redis instances create smartsupport-redis \
     --size=1 \
     --region=europe-west3 \
     --network=default
   ```

2. **Get Redis IP**
   ```bash
   gcloud redis instances describe smartsupport-redis --region=europe-west3
   ```

3. **Configure VPC Connector**
   - Create VPC connector in Cloud Run
   - Update Cloud Run service to use the connector
   - Set `REDIS_HOST` environment variable to Redis IP

4. **Update Cloud Run Service**
   ```bash
   gcloud run services update smartsupport-backend \
     --vpc-connector redis-connector \
     --update-env-vars REDIS_HOST=REDIS_IP_ADDRESS
   ```

### Post-Deployment Verification

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe smartsupport-backend \
  --region europe-west3 \
  --format 'value(status.url)')

# Test health endpoint
curl $SERVICE_URL/health

# Test API (replace YOUR_API_KEY)
curl -X POST "$SERVICE_URL/api/v1/tickets" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "I lost my card, please help"}'
```

## API Documentation

### Base URL
- **Local**: `http://localhost:8000`
- **Cloud Run**: `https://your-service-url.run.app`

### Authentication

All ticket endpoints require an API key in the `X-API-Key` header:

```bash
-H "X-API-Key: your-api-key-here"
```

### Endpoints

#### `GET /`
Root health check endpoint.

**Response:**
```json
{
  "message": "SmartSupport Backend API",
  "version": "1.0.0",
  "status": "healthy"
}
```

#### `GET /health`
Detailed health check with model status.

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "translation_enabled": true
}
```

#### `POST /api/v1/tickets`
Create a new ticket classification task.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/tickets" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"text": "I need help with my account balance"}'
```

**Response (202 Accepted):**
```json
{
  "task_id": "abc123-def456-...",
  "status": "PENDING",
  "message": "Ticket classification task created successfully"
}
```

**Rate Limit:** 5 requests per minute per IP address.

#### `GET /api/v1/tickets/status/{task_id}`
Get task status and result.

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/tickets/status/abc123-def456-..." \
  -H "X-API-Key: your-api-key"
```

**Response (when completed):**
```json
{
  "task_id": "abc123-def456-...",
  "status": "SUCCESS",
  "result": {
    "language": "en",
    "intent": "balance",
    "confidence": 0.95,
    "predictions": [
      {"label": "balance", "score": 0.95},
      {"label": "transfer_timing", "score": 0.03},
      {"label": "card_payment_fee_charged", "score": 0.02}
    ],
    "sanitized_text": "I need help with my account balance",
    "response_text": "I am checking your account balance. Your balance information is being prepared.",
    "translated_text": null,
    "prediction_details": "[{\"label\":\"balance\",\"score\":0.95},...]"
  },
  "error": null
}
```

#### `GET /api/v1/stats`
Get system statistics.

**Response:**
```json
{
  "total_tickets": 150,
  "active_tasks": 0,
  "success_rate": 0.98
}
```

#### `GET /api/v1/history?limit=10`
Get ticket processing history.

**Response:**
```json
[
  {
    "id": 1,
    "text": "Masked text...",
    "sanitized_text": "Masked text...",
    "intent": "balance",
    "confidence": 0.95,
    "language": "en",
    "response_text": "I am checking your account balance...",
    "translated_text": null,
    "prediction_details": "[{\"label\":\"balance\",\"score\":0.95},...]",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

## Testing

### Unit Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_api.py::test_create_ticket

# Run with coverage
pytest --cov=app tests/
```

### Load Testing with Locust

```bash
# Install Locust
pip install locust

# Start Locust
locust -f locustfile.py --host=http://localhost:8000

# Open browser: http://localhost:8089
# Configure: Number of users, spawn rate, then start swarming
```

**Command-line mode:**
```bash
locust -f locustfile.py --host=http://localhost:8000 \
  --headless \
  --users 10 \
  --spawn-rate 2 \
  --run-time 60s
```

## Project Structure

```
smartsupport-backend/
├── app/                    # Main application package
│   ├── core/              # Core functionality (config, db, security)
│   ├── models/            # Data models (schemas, SQL models)
│   ├── services/          # Business logic (ML, PII masking, responses)
│   ├── worker/            # Celery worker tasks
│   └── main.py            # FastAPI application entry point
├── tests/                 # Test suite
├── reports/               # Test reports and documentation
├── .dockerignore          # Docker build exclusions
├── .gcloudignore          # Google Cloud Build exclusions
├── cloudbuild.yaml        # Google Cloud Build configuration
├── docker-compose.yml     # Local development orchestration
├── Dockerfile             # Container image definition
├── locustfile.py          # Load testing configuration
├── pytest.ini             # Pytest configuration
├── requirements.txt       # Python dependencies
├── start.sh               # Container startup script
└── README.md              # This file
```

See `PROJECT_STRUCTURE.md` for detailed structure documentation.

## Development Guidelines

### Code Style
- Follow PEP 8 Python style guide
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes

### Adding New Features
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes following existing patterns
3. Add tests for new functionality
4. Update documentation if needed
5. Submit pull request

### Database Migrations
The application automatically migrates the database schema on startup. For new columns:
1. Add column to `app/models/sql_models.py`
2. Update `app/core/db.py` migration logic if needed
3. Restart the application

## Troubleshooting

### Local Development Issues

**Port already in use:**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or change port in docker-compose.yml
```

**Redis connection errors:**
```bash
# Check Redis is running
docker-compose ps redis

# Check Redis logs
docker-compose logs redis

# Restart Redis
docker-compose restart redis
```

**Model loading errors:**
- First load may take 2-3 minutes (downloading models)
- Check internet connection
- Verify Hugging Face access
- Check Docker logs: `docker-compose logs backend`

### Cloud Run Issues

**Container fails to start:**
- Check Cloud Run logs: `gcloud run services logs read smartsupport-backend`
- Verify environment variables are set
- Check memory/CPU limits (may need to increase)

**Rate limiting too aggressive:**
- Adjust rate limit in `app/main.py`: `@limiter.limit("5/minute")`
- Redeploy after changes

**Redis connection issues:**
- Verify VPC connector is configured
- Check Redis instance is in same region
- Verify firewall rules allow Cloud Run → Redis

**Build timeout:**
- Build may take 20-30 minutes first time (downloading models)
- `cloudbuild.yaml` timeout is set to 3600s (1 hour)
- Subsequent builds are faster due to Docker layer caching

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEY` | `CHANGE_ME_IN_PRODUCTION` | Secret API key for authentication |
| `REDIS_HOST` | `redis` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |
| `REDIS_DB` | `0` | Redis database number |
| `DEBUG` | `False` | Enable debug mode |
| `PORT` | `8000` | Server port (Cloud Run uses 8080) |

For issues and questions:
- Open an issue on GitHub
- Check `DEPLOYMENT.md` for deployment-specific help
- Review `TEST_RESULTS.md` for test documentation
