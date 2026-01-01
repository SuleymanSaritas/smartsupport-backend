# SmartSupport Backend API

Production-ready FastAPI backend for multi-lingual customer support ticket classification system.

## Features

- **Multi-lingual Support**: Automatically detects Turkish or English and routes to appropriate AI model
- **PII Masking**: Masks sensitive information including Turkish Identity Numbers (TCKN), emails, and phone numbers
- **Async Processing**: Uses Celery + Redis for asynchronous ticket processing
- **Dockerized**: Fully containerized with Docker Compose
- **Production Ready**: Includes proper error handling, logging, and API key authentication

## Tech Stack

- **Framework**: FastAPI (Python 3.9+)
- **Async Processing**: Celery + Redis
- **ML Libraries**: transformers, torch, langdetect
- **PII Masking**: presidio-analyzer, presidio-anonymizer
- **Models**:
  - Turkish: `yeniguno/bert-uncased-turkish-intent-classification`
  - English: `mrm8488/distilroberta-finetuned-banking77`

## Project Structure

```
smartsupport-backend/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI app, CORS middleware, Routes
│   ├── core/
│   │   ├── config.py      # Env vars (Settings)
│   │   └── security.py    # Simple API Key validation
│   ├── models/
│   │   └── schemas.py     # Pydantic models
│   ├── services/
│   │   ├── model_manager.py # Singleton class to load BOTH models
│   │   └── guardrails.py    # PII Masking logic
│   └── worker/
│       ├── celery_app.py  # Celery configuration
│       └── tasks.py       # The async task that runs inference
├── .env.example
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Quick Start

### 1. Environment Setup

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and set your `API_KEY`.

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

This will start:
- **Redis** on port 6379
- **Backend API** on port 8000
- **Celery Worker** for async processing

### 3. API Usage

#### Create a Ticket Classification Task

```bash
curl -X POST "http://localhost:8000/api/v1/tickets" \
  -H "X-API-Key: your-secret-api-key-here-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{"text": "I need help with my account balance"}'
```

Response:
```json
{
  "task_id": "abc123-def456-...",
  "status": "PENDING",
  "message": "Ticket classification task created successfully"
}
```

#### Check Task Status

```bash
curl -X GET "http://localhost:8000/api/v1/tickets/status/{task_id}" \
  -H "X-API-Key: your-secret-api-key-here-change-in-production"
```

Response (when completed):
```json
{
  "task_id": "abc123-def456-...",
  "status": "SUCCESS",
  "result": {
    "language": "en",
    "intent": "check_account_balance",
    "confidence": 0.95,
    "sanitized_text": "I need help with my account balance"
  },
  "error": null
}
```

## API Endpoints

- `GET /` - Root health check
- `GET /health` - Health check with model status
- `POST /api/v1/tickets` - Create ticket classification task (requires API key)
- `GET /api/v1/tickets/status/{task_id}` - Get task status and result (requires API key)

## Development

### Local Development (without Docker)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start Redis:
```bash
redis-server
```

3. Start the backend:
```bash
uvicorn app.main:app --reload
```

4. Start the worker (in another terminal):
```bash
celery -A app.worker.celery_app worker --loglevel=info
```

## Notes

- Models are loaded once at startup (Singleton pattern) to optimize memory
- PII masking includes custom regex for Turkish Identity Numbers (TCKN)
- All tasks are processed asynchronously via Celery
- API key authentication is required for all ticket endpoints




