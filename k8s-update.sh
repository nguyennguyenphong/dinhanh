#!/bin/bash
# Kubernetes Update Script
set -e

NAMESPACE="dinhanh"
REGISTRY="${REGISTRY:-your-registry}"
IMAGE_NAME="${REGISTRY}/dinhanh"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "🔄 Updating Dinhanh deployment..."

# Build and push image
echo "📦 Building new Docker image..."
docker build -f Dockerfile.k8s -t "${IMAGE_NAME}:${IMAGE_TAG}" .

echo "📤 Pushing image to registry..."
docker push "${IMAGE_NAME}:${IMAGE_TAG}"

# Update deployments
echo "🔄 Rolling out new deployment..."
kubectl rollout restart deployment/django-web -n $NAMESPACE
kubectl rollout restart deployment/celery-worker -n $NAMESPACE
kubectl rollout restart deployment/celery-beat -n $NAMESPACE

# Wait for rollout
echo "⏳ Waiting for rollout..."
kubectl rollout status deployment/django-web -n $NAMESPACE --timeout=600s
kubectl rollout status deployment/celery-worker -n $NAMESPACE --timeout=600s

echo "✅ Update complete!"
