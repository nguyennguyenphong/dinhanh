# Kubernetes Deployment Guide - Production Setup

## 📋 Điều kiện tiên quyết

- Kubernetes cluster (1.24+)
- kubectl CLI tool
- Docker registry (DockerHub, ECR, GCR, etc.)
- cert-manager (cho HTTPS)
- nginx-ingress-controller

## 🔧 Cấu hình trước khi deploy

### 1. Cập nhật credentials

**File: `k8s/02-secret.yaml`**
```bash
# Thay đổi giá trị sau:
- SECRET_KEY: Django secret key (dùng: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
- DB_PASSWORD: Strong password cho PostgreSQL
- EMAIL_HOST_PASSWORD: Email app password
- AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY: Nếu dùng AWS S3
```

### 2. Cập nhật configuration

**File: `k8s/01-configmap.yaml`**
```bash
- ALLOWED_HOSTS: Thay đổi thành domain của bạn
- TIME_ZONE & LANGUAGE_CODE: Tùy theo yêu cầu
```

### 3. Cập nhật Docker image

**File: `k8s/05-django-web.yaml`, `k8s/06-celery-worker.yaml`, etc.**
```bash
# Thay đổi:
image: your-registry/dinhanh:latest
# Ví dụ:
image: gcr.io/my-project/dinhanh:v1.0.0
```

### 4. Cập nhật Ingress domain

**File: `k8s/08-ingress.yaml`**
```bash
- example.com -> your-actual-domain.com
```

## 🚀 Deployment Steps

### 1. Build và Push Docker Image

```bash
# Build image cho K8s
docker build -f Dockerfile.k8s -t your-registry/dinhanh:latest .

# Push to registry
docker push your-registry/dinhanh:latest
```

### 2. Setup Cert-Manager (cho HTTPS)

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer cho Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### 3. Deploy Application

```bash
# Tự động (recommended)
chmod +x k8s-deploy.sh
./k8s-deploy.sh

# Manual
kubectl apply -f k8s/
```

### 4. Verify Deployment

```bash
# Check all resources
kubectl get all -n dinhanh

# Check pod logs
kubectl logs -n dinhanh -l app=django-web --tail=50 -f

# Check ingress
kubectl get ingress -n dinhanh

# Test application
kubectl port-forward -n dinhanh svc/django-web 8000:80
# Access: http://localhost:8000
```

## 📈 Scaling & Monitoring

### Horizontal Pod Autoscaling

```bash
# View HPA status
kubectl get hpa -n dinhanh

# Manual scaling
kubectl scale deployment/django-web -n dinhanh --replicas=5
```

### View Logs

```bash
# Django web logs
kubectl logs -n dinhanh -l app=django-web --tail=100 -f

# Celery worker logs
kubectl logs -n dinhanh -l app=celery-worker --tail=100 -f

# Celery beat logs
kubectl logs -n dinhanh -l app=celery-beat --tail=100 -f

# Combined logs
kubectl logs -n dinhanh -l tier=web --all-containers=true -f
```

### Database Maintenance

```bash
# Connect to PostgreSQL
kubectl exec -it -n dinhanh $(kubectl get pod -n dinhanh -l app=postgres -o jsonpath='{.items[0].metadata.name}') -- psql -U dinhanh_user -d dinhanh_db

# Database backup
kubectl exec -n dinhanh $(kubectl get pod -n dinhanh -l app=postgres -o jsonpath='{.items[0].metadata.name}') -- pg_dump -U dinhanh_user dinhanh_db > backup.sql

# Database restore
kubectl exec -i -n dinhanh $(kubectl get pod -n dinhanh -l app=postgres -o jsonpath='{.items[0].metadata.name}') -- psql -U dinhanh_user dinhanh_db < backup.sql
```

## 🔄 Updating Application

```bash
# Option 1: Automated
chmod +x k8s-update.sh
./k8s-update.sh

# Option 2: Manual
docker build -f Dockerfile.k8s -t your-registry/dinhanh:v1.1.0 .
docker push your-registry/dinhanh:v1.1.0
kubectl set image deployment/django-web django=your-registry/dinhanh:v1.1.0 -n dinhanh
kubectl rollout status deployment/django-web -n dinhanh
```

## 🛑 Cleanup

```bash
# Delete entire namespace (all resources deleted)
kubectl delete namespace dinhanh

# Delete specific resource
kubectl delete deployment django-web -n dinhanh
```

## ⚙️ Advanced Configuration

### Resource Requests & Limits

Điều chỉnh trong từng `deployment.yaml`:
```yaml
resources:
  requests:
    cpu: 500m        # Minimum guaranteed CPU
    memory: 512Mi    # Minimum guaranteed memory
  limits:
    cpu: 1000m       # Maximum CPU
    memory: 1Gi      # Maximum memory
```

### Storage Classes

Cho production, sử dụng:
- AWS EBS: `storageClassName: ebs-sc`
- GCP Persistent Disk: `storageClassName: pd-standard`
- Azure Disk: `storageClassName: managed-premium`

Tạo storage class custom:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
```

### Network Policies

Đã include trong `k8s/09-pdb.yaml`. Cấu hình thêm:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: dinhanh
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

## 📊 Monitoring & Logging

### Prometheus Integration

```bash
# Add annotation to enable scraping
kubectl annotate deployment django-web \
  prometheus.io/scrape=true \
  prometheus.io/port=8000 \
  prometheus.io/path=/metrics/ \
  -n dinhanh
```

### ELK Stack (Optional)

Deploy Elasticsearch, Logstash, Kibana cho centralized logging.

## 🚨 Troubleshooting

### Pod không start

```bash
# Check events
kubectl describe pod POD_NAME -n dinhanh

# Check logs
kubectl logs POD_NAME -n dinhanh --previous
```

### Persistent Volume không mount

```bash
# Check PVC status
kubectl get pvc -n dinhanh

# Check PV status
kubectl get pv

# Describe PVC
kubectl describe pvc static-pvc -n dinhanh
```

### Database connection errors

```bash
# Test PostgreSQL connectivity
kubectl exec -it deployment/django-web -n dinhanh -- python manage.py dbshell

# Check service DNS
kubectl exec -it deployment/django-web -n dinhanh -- nslookup postgres.dinhanh.svc.cluster.local
```

## 📚 Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Django on Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Cert-Manager Docs](https://cert-manager.io/docs/)
