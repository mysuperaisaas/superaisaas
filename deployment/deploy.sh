#!/bin/bash

# MySuperAISaaS Deployment Script
# Deploy to GCP infrastructure

set -e

PROJECT_ID="aisaas-project" #OR Within the second backup project : aisaas-secondary-project
REGION="northamerica-northeast1"
SERVICE_NAME="mysuperaisaas-api"

echo "🚀 Starting deployment for MySuperAISaaS..."

# Authenticate with GCP
echo "Authenticating with GCP..."
gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS

# Set project
gcloud config set project $PROJECT_ID

# Build and push Docker image
echo "Building Docker image..."
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .

echo "Pushing to Container Registry..."
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 100 \
    --min-instances 2

# Deploy Cloud Functions
echo "Deploying Cloud Functions..."
cd cloud_functions

gcloud functions deploy process-financial-data \
    --runtime python39 \
    --trigger-http \
    --entry-point process_financial_data \
    --memory 512MB \
    --timeout 60s \
    --region $REGION

cd ..

echo "✅ Deployment completed successfully!"
echo "API URL: https://$SERVICE_NAME-$REGION.run.app"