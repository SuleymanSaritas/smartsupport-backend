#!/bin/bash
# DVC Setup Script for SmartSupport Backend
# This script initializes DVC and sets up remote storage

echo "Setting up DVC for SmartSupport Backend..."

# Check if DVC is installed
if ! command -v dvc &> /dev/null; then
    echo "DVC is not installed. Installing..."
    pip install dvc
fi

# Initialize DVC if not already initialized
if [ ! -d ".dvc" ]; then
    echo "Initializing DVC..."
    dvc init
    echo "DVC initialized successfully."
else
    echo "DVC already initialized."
fi

# Prompt for remote storage type
echo ""
echo "Choose remote storage type:"
echo "1) Google Cloud Storage (GCS)"
echo "2) Google Drive"
echo "3) Skip (configure manually later)"
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        read -p "Enter GCS bucket name (e.g., your-bucket-name/dvc-storage): " bucket
        dvc remote add -d gcs "gs://${bucket}"
        echo "GCS remote configured: gs://${bucket}"
        echo "Note: Ensure you have GCS credentials configured (gcloud auth application-default login)"
        ;;
    2)
        read -p "Enter Google Drive folder ID: " folder_id
        dvc remote add -d gdrive "gdrive://${folder_id}"
        echo "Google Drive remote configured: gdrive://${folder_id}"
        echo "Note: You'll need to authenticate with Google Drive on first use"
        ;;
    3)
        echo "Skipping remote configuration. Configure manually in .dvc/config"
        ;;
    *)
        echo "Invalid choice. Skipping remote configuration."
        ;;
esac

echo ""
echo "DVC setup complete!"
echo ""
echo "To track files with DVC:"
echo "  dvc add path/to/large-file"
echo "  git add path/to/large-file.dvc .gitignore"
echo "  git commit -m 'Track file with DVC'"
echo ""
echo "To pull tracked files:"
echo "  dvc pull"

