# Deployment Guide

## GitHub Setup

### 1. Initialize Git Repository

```bash
git init
git add .
git commit -m "Initial commit: SmartSupport Backend API"
git branch -M main
git remote add origin https://github.com/your-username/smartsupport-backend.git
git push -u origin main
```

### 2. DVC Setup for Large Files

DVC (Data Version Control) is used to track large files like ML models without bloating the Git repository.

#### Initialize DVC

**Option 1: Use setup script (Recommended)**

```bash
# On Linux/Mac
chmod +x setup-dvc.sh
./setup-dvc.sh

# On Windows (PowerShell)
.\setup-dvc.ps1
```

**Option 2: Manual setup**

```bash
# Install DVC
pip install dvc

# Initialize DVC in the repository
dvc init

# Add remote storage (Google Cloud Storage)
dvc remote add -d gcs gs://your-bucket-name/dvc-storage

# Or use Google Drive
# dvc remote add -d gdrive gdrive://your-folder-id

# Authenticate (for GCS)
gcloud auth application-default login
```

#### Track Models with DVC

```bash
# If you want to track specific model files
# dvc add app/models/
# git add app/models/.gitignore app/models.dvc
# git commit -m "Track models with DVC"
```

#### Pull Models in Production

```bash
# Pull models from DVC remote
dvc pull
```

## Google Cloud Deployment

### Prerequisites

1. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install
2. Authenticate: `gcloud auth login`
3. Set project: `gcloud config set project YOUR_PROJECT_ID`

### Option 1: Deploy via Cloud Build (Recommended)

```bash
# Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml
```

### Option 2: Deploy via Cloud Run CLI

```bash
# Build and deploy directly
gcloud run deploy smartsupport-backend \
  --source . \
  --region us-central1 \
  --platform managed \
  --port 8080 \
  --memory 4Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10 \
  --set-env-vars "API_KEY=your-api-key,PORT=8080"
```

### Option 3: Deploy via Docker

```bash
# Build Docker image
docker build -t gcr.io/YOUR_PROJECT_ID/smartsupport-backend .

# Push to Container Registry
docker push gcr.io/YOUR_PROJECT_ID/smartsupport-backend

# Deploy to Cloud Run
gcloud run deploy smartsupport-backend \
  --image gcr.io/YOUR_PROJECT_ID/smartsupport-backend \
  --region us-central1 \
  --platform managed \
  --port 8080
```

### Environment Variables

Set these in Cloud Run console or via gcloud:

```bash
gcloud run services update smartsupport-backend \
  --update-env-vars API_KEY=your-api-key,REDIS_HOST=your-redis-instance
```

### Redis Setup (Cloud Memorystore)

1. Create Redis instance in Cloud Memorystore
2. Update `REDIS_HOST` environment variable with the instance IP
3. Ensure Cloud Run service has access to the VPC

### Health Checks

The application exposes health check endpoints:
- `GET /health` - Health check with model status
- `GET /` - Root health check

Configure these in Cloud Run for automatic health monitoring.

## Local Development

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Notes

- Port 8080 is used for Google Cloud Run (default)
- Port 8000 is used for local development
- Models are downloaded on first use (lazy loading)
- Database is SQLite (consider Cloud SQL for production)
- Redis is required for Celery task queue

