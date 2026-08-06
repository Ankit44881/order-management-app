#!/bin/bash

set -e

# -----------------------------
# Configuration
# -----------------------------
PROJECT_ID="project-e88d1c23-e44c-4d58-8dd"
REGION="us-central1"
ZONE="us-central1-b"

CLUSTER_NAME="gke-cluster"
REPOSITORY_NAME="om-app-repo"

echo "====================================="
echo "Setting GCP Project"
echo "====================================="
gcloud config set project $PROJECT_ID

echo "====================================="
echo "Enabling Required APIs"
echo "====================================="
gcloud services enable \
    container.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com

echo "====================================="
echo "Creating Artifact Registry"
echo "====================================="
if ! gcloud artifacts repositories describe $REPOSITORY_NAME --location=$REGION >/dev/null 2>&1; then
    gcloud artifacts repositories create $REPOSITORY_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="Docker Repository for Chai Politics"
    echo "✅ Artifact Registry created."
else
    echo "ℹ️ Artifact Registry '$REPOSITORY_NAME' already exists. Skipping creation."
fi

echo "====================================="
echo "Configuring Docker Credentials"
echo "====================================="
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

echo "====================================="
echo "Creating GKE Cluster"
echo "====================================="
if ! gcloud container clusters describe $CLUSTER_NAME --zone=$ZONE >/dev/null 2>&1; then
    gcloud container clusters create $CLUSTER_NAME \
        --machine-type="e2-medium" \
        --zone=$ZONE \
        --num-nodes=1
    echo "✅ GKE Cluster created."
else
    echo "ℹ️ GKE Cluster '$CLUSTER_NAME' already exists. Skipping creation."
fi

echo "====================================="
echo "Getting Cluster Credentials"
echo "====================================="
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE

echo "====================================="
echo "Cluster Status Verification"
echo "====================================="
kubectl get nodes

echo ""
echo "✅ Setup Completed Successfully!"