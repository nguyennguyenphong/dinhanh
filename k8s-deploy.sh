#!/bin/bash
# Kubernetes Deployment Script
set -e

NAMESPACE="dinhanh"
REGISTRY="${REGISTRY:-your-registry}"
IMAGE_NAME="${REGISTRY}/dinhanh"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "🚀 Deploying Dinhanh to Kubernetes..."

# Build and push image
echo "📦 Building Docker image..."
docker build -f Dockerfile.k8s -t "${IMAGE_NAME}:${IMAGE_TAG}" .

echo "📤 Pushing image to registry..."
docker push "${IMAGE_NAME}:${IMAGE_TAG}"

# Create namespace
echo "🔧 Creating namespace..."
kubectl apply -f k8s/00-namespace.yaml

# Create secrets and configmaps
echo "🔐 Configuring secrets and configs..."
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secret.yaml

# Deploy infrastructure (PostgreSQL, Redis)
echo "🗄️  Deploying PostgreSQL and Redis..."
kubectl apply -f k8s/03-postgres.yaml
kubectl apply -f k8s/04-redis.yaml

# Wait for databases to be ready
echo "⏳ Waiting for databases..."
kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s || true
kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s || true

sleep 10

# Deploy Django web
echo "🌐 Deploying Django web service..."
kubectl apply -f k8s/05-django-web.yaml

# Deploy Celery workers
echo "⚙️  Deploying Celery workers..."
kubectl apply -f k8s/06-celery-worker.yaml
kubectl apply -f k8s/07-celery-beat.yaml

# Configure networking
echo "🔗 Configuring ingress and networking..."
kubectl apply -f k8s/08-ingress.yaml
kubectl apply -f k8s/09-pdb.yaml

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl rollout status deployment/django-web -n $NAMESPACE --timeout=600s
kubectl rollout status deployment/celery-worker -n $NAMESPACE --timeout=600s

# Print status
echo "✅ Deployment complete!"
echo ""
echo "📊 Deployment Status:"
kubectl get all -n $NAMESPACE

echo ""
echo "🌍 Ingress Info:"
kubectl get ingress -n $NAMESPACE

echo ""
echo "💡 Useful Commands:"
echo "  - View logs: kubectl logs -n $NAMESPACE -l app=django-web --tail=100 -f"
echo "  - Scale deployment: kubectl scale deployment/django-web -n $NAMESPACE --replicas=5"
echo "  - Port forward: kubectl port-forward -n $NAMESPACE svc/django-web 8000:80"
