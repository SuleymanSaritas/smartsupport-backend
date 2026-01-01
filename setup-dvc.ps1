# DVC Setup Script for SmartSupport Backend (PowerShell)
# This script initializes DVC and sets up remote storage

Write-Host "Setting up DVC for SmartSupport Backend..." -ForegroundColor Green

# Check if DVC is installed
try {
    $null = Get-Command dvc -ErrorAction Stop
    Write-Host "DVC is installed." -ForegroundColor Green
} catch {
    Write-Host "DVC is not installed. Installing..." -ForegroundColor Yellow
    pip install dvc
}

# Initialize DVC if not already initialized
if (-not (Test-Path ".dvc")) {
    Write-Host "Initializing DVC..." -ForegroundColor Green
    dvc init
    Write-Host "DVC initialized successfully." -ForegroundColor Green
} else {
    Write-Host "DVC already initialized." -ForegroundColor Yellow
}

# Prompt for remote storage type
Write-Host ""
Write-Host "Choose remote storage type:" -ForegroundColor Cyan
Write-Host "1) Google Cloud Storage (GCS)"
Write-Host "2) Google Drive"
Write-Host "3) Skip (configure manually later)"
$choice = Read-Host "Enter choice [1-3]"

switch ($choice) {
    "1" {
        $bucket = Read-Host "Enter GCS bucket name (e.g., your-bucket-name/dvc-storage)"
        dvc remote add -d gcs "gs://$bucket"
        Write-Host "GCS remote configured: gs://$bucket" -ForegroundColor Green
        Write-Host "Note: Ensure you have GCS credentials configured (gcloud auth application-default login)" -ForegroundColor Yellow
    }
    "2" {
        $folder_id = Read-Host "Enter Google Drive folder ID"
        dvc remote add -d gdrive "gdrive://$folder_id"
        Write-Host "Google Drive remote configured: gdrive://$folder_id" -ForegroundColor Green
        Write-Host "Note: You'll need to authenticate with Google Drive on first use" -ForegroundColor Yellow
    }
    "3" {
        Write-Host "Skipping remote configuration. Configure manually in .dvc/config" -ForegroundColor Yellow
    }
    default {
        Write-Host "Invalid choice. Skipping remote configuration." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "DVC setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To track files with DVC:" -ForegroundColor Cyan
Write-Host "  dvc add path/to/large-file"
Write-Host "  git add path/to/large-file.dvc .gitignore"
Write-Host "  git commit -m 'Track file with DVC'"
Write-Host ""
Write-Host "To pull tracked files:" -ForegroundColor Cyan
Write-Host "  dvc pull"

