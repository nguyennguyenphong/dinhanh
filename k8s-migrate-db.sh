#!/bin/bash
# Database Migration Script for Kubernetes
set -e

NAMESPACE="dinhanh"

echo "🔄 Running database migrations..."

# Get django-web pod
POD=$(kubectl get pod -n $NAMESPACE -l app=django-web -o jsonpath='{.items[0].metadata.name}')

if [ -z "$POD" ]; then
    echo "❌ No django-web pod found!"
    exit 1
fi

echo "📌 Using pod: $POD"

# Run migrations
echo "🏃 Running migrations..."
kubectl exec -n $NAMESPACE $POD -- python manage.py migrate

# Collect static files
echo "📦 Collecting static files..."
kubectl exec -n $NAMESPACE $POD -- python manage.py collectstatic --noinput

# Create superuser (optional)
read -p "Create superuser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    kubectl exec -it -n $NAMESPACE $POD -- python manage.py createsuperuser
fi

echo "✅ Database setup complete!"
echo ""
echo "📊 Database info:"
kubectl exec -n $NAMESPACE $POD -- python manage.py dbshell -c "SELECT version();"

echo ""
echo "💡 Next steps:"
echo "  1. Access Django admin: https://your-domain.com/admin"
echo "  2. Setup site domain: https://your-domain.com/admin/sites/"
echo "  3. Configure email: https://your-domain.com/admin/account/emailaddress/"
