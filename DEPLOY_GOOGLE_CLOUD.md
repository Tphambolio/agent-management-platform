# Deploy to Google Cloud Platform (GCP)

## Prerequisites
- Google Cloud account
- gcloud CLI installed
- Project created in GCP

## Installation

```bash
# Install gcloud CLI on Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

## Deploy Backend to Google Cloud Run

### Step 1: Create Dockerfile for Backend
The `Dockerfile.backend` is already created in the repo.

### Step 2: Build and Deploy

```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Navigate to backend directory
cd /home/user/wildfire-simulator-v2/agent-management-platform

# Build and deploy backend
gcloud run deploy agent-management-backend \
  --source . \
  --dockerfile Dockerfile.backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "DEBUG=false,HOST=0.0.0.0,PORT=8080" \
  --memory 1Gi \
  --cpu 1

# Get the backend URL
gcloud run services describe agent-management-backend \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

## Deploy Frontend to Google Cloud Storage + Cloud Run

### Option A: Static Hosting (Cheaper)

```bash
# Build frontend
cd frontend
npm install
npm run build

# Create storage bucket
gsutil mb gs://agent-management-frontend

# Upload built files
gsutil -m cp -r dist/* gs://agent-management-frontend

# Make it public
gsutil iam ch allUsers:objectViewer gs://agent-management-frontend

# Enable website hosting
gsutil web set -m index.html -e index.html gs://agent-management-frontend
```

### Option B: Cloud Run (Better for SPAs)

```bash
# From agent-management-platform directory
gcloud run deploy agent-management-frontend \
  --source . \
  --dockerfile Dockerfile.frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 80

# Get the frontend URL
gcloud run services describe agent-management-frontend \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

## Update CORS Settings

```bash
# Get backend URL
BACKEND_URL=$(gcloud run services describe agent-management-backend \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)')

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe agent-management-frontend \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)')

# Update backend CORS
gcloud run services update agent-management-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars "CORS_ORIGINS=${FRONTEND_URL}"

# Update frontend API URL
cd frontend
echo "VITE_API_URL=${BACKEND_URL}" > .env.production
npm run build

# Redeploy frontend with updated config
gcloud run deploy agent-management-frontend \
  --source . \
  --dockerfile Dockerfile.frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Set Environment Variables

```bash
# For backend
gcloud run services update agent-management-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars "DEBUG=false,CORS_ORIGINS=https://your-frontend-url" \
  --set-secrets "ANTHROPIC_API_KEY=projects/YOUR_PROJECT/secrets/anthropic-key:latest"
```

## Cost Estimate

Google Cloud Run pricing:
- **Free tier**: 2 million requests/month, 360,000 GB-seconds
- **Paid**: ~$0.40 per million requests
- **Estimated**: $0-5/month for light usage

## Useful Commands

```bash
# View logs
gcloud run services logs read agent-management-backend --limit 50

# List services
gcloud run services list

# Delete service
gcloud run services delete agent-management-backend

# Check deployment status
gcloud run services describe agent-management-backend
```

## Troubleshooting

### "Permission denied" errors
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### "Service not found"
```bash
# Make sure you're in the right region
gcloud config set run/region us-central1
```

### Build fails
```bash
# Check build logs
gcloud builds list --limit 5
gcloud builds log BUILD_ID
```

## Your URLs

After deployment:
- **Backend**: `https://agent-management-backend-HASH-uc.a.run.app`
- **Frontend**: `https://agent-management-frontend-HASH-uc.a.run.app`
- **API Docs**: `https://agent-management-backend-HASH-uc.a.run.app/docs`
