# Project Structure

This document describes the organization of the SmartSupport Backend project.

## Directory Layout

```
smartsupport-backend/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry point
│   ├── core/                    # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration and settings
│   │   ├── db.py                # Database connection and session management
│   │   └── security.py          # API key validation
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   ├── schemas.py           # Pydantic schemas for API
│   │   └── sql_models.py        # SQLAlchemy database models
│   ├── services/                 # Business logic services
│   │   ├── __init__.py
│   │   ├── guardrails.py        # PII masking service
│   │   ├── model_manager.py     # ML model management
│   │   └── response_generator.py # Natural language response generation
│   └── worker/                   # Celery worker tasks
│       ├── __init__.py
│       ├── celery_app.py        # Celery application configuration
│       └── tasks.py             # Async task definitions
│
├── tests/                        # Test suite
│   ├── __init__.py
│   └── test_api.py              # API endpoint tests
│
├── reports/                      # Test reports and documentation
│   ├── Final_Ratio_Result.png
│   ├── Locust_Charts.png
│   └── Locust_Test_Report.png
│
├── .dockerignore                 # Docker build exclusions
├── .gcloudignore                 # Google Cloud Build exclusions
├── .gitignore                    # Git exclusions
├── cloudbuild.yaml               # Google Cloud Build configuration
├── DEPLOYMENT.md                 # Deployment guide
├── docker-compose.yml            # Local development orchestration
├── Dockerfile                    # Container image definition
├── dvc.yaml                      # DVC pipeline configuration
├── locustfile.py                 # Load testing configuration
├── pytest.ini                    # Pytest configuration
├── README.md                     # Project documentation
├── requirements.txt              # Python dependencies
├── setup-dvc.ps1                 # DVC setup script (Windows)
├── setup-dvc.sh                  # DVC setup script (Unix)
├── start.sh                      # Container startup script
└── TEST_RESULTS.md               # Test results documentation
```

## Structure Principles

### Separation of Concerns
- **`app/core/`**: Infrastructure concerns (config, database, security)
- **`app/models/`**: Data layer (schemas and database models)
- **`app/services/`**: Business logic (ML, PII masking, responses)
- **`app/worker/`**: Asynchronous task processing

### Industry Standards
- Follows FastAPI best practices
- Clear separation between API, business logic, and data layers
- Test suite in dedicated `tests/` directory
- Configuration management via environment variables
- Docker containerization for deployment

### File Organization
- Each module has clear, single responsibility
- Related functionality grouped in packages
- Configuration files at root level
- Documentation and reports in dedicated directories

