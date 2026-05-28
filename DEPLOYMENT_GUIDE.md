# Production Deployment Configuration - Complete Guide

## 📦 Files Created

### Docker Files
- **Dockerfile.prod** - Docker image cho Docker Compose
- **Dockerfile.k8s** - Docker image tối ưu cho Kubernetes
- **docker-compose.prod.yaml** - Production Docker Compose orchestration
- **.dockerignore** - Optimize Docker image size

### Kubernetes Manifests (k8s/)
- **00-namespace.yaml** - Kubernetes namespace
- **01-configmap.yaml** - Application configuration
- **02-secret.yaml** - Sensitive data (credentials)
- **03-postgres.yaml** - PostgreSQL deployment + service + PVC
- **04-redis.yaml** - Redis deployment + service + PVC
- **05-django-web.yaml** - Django web + service + HPA + PVCs
- **06-celery-worker.yaml** - Celery workers + HPA
- **07-celery-beat.yaml** - Celery scheduler
- **08-ingress.yaml** - Ingress routing + TLS
- **09-pdb.yaml** - Pod Disruption Budgets

### Deployment Scripts
- **k8s-deploy.sh** - Full deployment script
- **k8s-update.sh** - Update deployment script
- **k8s-update-db.sh** - Database migration script

### Documentation
- **K8S_DEPLOYMENT_GUIDE.md** - Chi tiết hướng dẫn K8s
- **HELM_GUIDE.md** - Hướng dẫn Helm Chart

### Configuration
- **.env.prod.example** - Environment variables template
- **docker/nginx/nginx.conf** - Nginx main configuration
- **docker/nginx/conf.d/default.conf** - Nginx virtual host

## 🎯 Quick Start

### Option 1: Docker Compose (Simple)

```bash
# 1. Copy env file
cp .env.prod.example .env.prod

# 2. Edit .env.prod với credentials của bạn
nano .env.prod

# 3. Build và deploy
docker-compose -f docker-compose.prod.yaml up -d

# 4. Check status
docker-compose -f docker-compose.prod.yaml ps
```

### Option 2: Kubernetes (Scalable)

```bash
# 1. Prepare
cp k8s/02-secret.yaml k8s/02-secret-prod.yaml
nano k8s/02-secret-prod.yaml  # Update credentials

# 2. Update configs
nano k8s/01-configmap.yaml     # Update ALLOWED_HOSTS, domains
nano k8s/05-django-web.yaml    # Update image: your-registry/dinhanh:latest
nano k8s/08-ingress.yaml       # Update domains

# 3. Deploy
chmod +x k8s-deploy.sh
REGISTRY=your-registry IMAGE_TAG=v1.0.0 ./k8s-deploy.sh

# 4. Check status
kubectl get all -n dinhanh
```

## 🔐 Security Checklist

✅ **Before Production:**

- [ ] Update SECRET_KEY in secrets
- [ ] Set strong DB_PASSWORD, EMAIL passwords
- [ ] Change ALLOWED_HOSTS to your domain
- [ ] Enable SECURE_SSL_REDIRECT = True
- [ ] Setup SSL certificates (Let's Encrypt)
- [ ] Configure firewall rules
- [ ] Setup backups for databases
- [ ] Enable monitoring and logging
- [ ] Use private Docker registry
- [ ] Enable CSRF protection
- [ ] Configure CORS properly
- [ ] Setup rate limiting in Nginx

## 📊 Architecture

```
┌─────────────────────────────────────────────┐
│         Load Balancer / Ingress             │
│  (nginx-ingress / AWS ELB / GCP LB)        │
└────────────────────┬────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    ┌───┴──┐     ┌───┴──┐    ┌───┴──┐
    │Django│     │Django│    │Django│  (Pods)
    │Web 1 │     │Web 2 │    │Web 3 │  (Replicated)
    └───┬──┘     └───┬──┘    └───┬──┘
        │            │            │
        └────────────┼────────────┘
                     │
        ┌────────────┼─────────────────┐
        │            │                 │
    ┌───┴──┐    ┌────┴─────┐    ┌─────┴──┐
    │Redis │    │PostgreSQL │    │Celery  │
    │Cache │    │Database   │    │Workers │
    └──────┘    └───────────┘    └────────┘
```

## 🚀 Deployment Comparison

| Aspect | Docker Compose | Kubernetes |
|--------|---|---|
| **Scale** | Single host | Multi-host |
| **HA** | No | Yes (built-in) |
| **Auto-restart** | Basic | Advanced |
| **Load Balancing** | No | Yes |
| **Rolling Updates** | Manual | Automatic |
| **Monitoring** | Limited | Advanced |
| **Cost** | Low | Medium-High |
| **Complexity** | Low | High |

## 📈 Production Setup Recommendations

### Minimum Resources
- 3 Kubernetes nodes (t3.medium or equivalent)
- SSD for databases (20GB+)
- Managed database for production (AWS RDS, GCP Cloud SQL)
- Separate cache cluster (Redis Enterprise)

### High Availability
- Multi-region deployment
- Geo-distributed Redis
- Database replication with failover
- Auto-scaling based on metrics
- Distributed logging (ELK, Datadog)

### Monitoring
- Prometheus for metrics
- Grafana for visualization
- AlertManager for alerts
- ELK or CloudWatch for logs
- Jaeger or Datadog for tracing

## 🔄 Maintenance Tasks

### Daily
```bash
# Check pod health
kubectl get pods -n dinhanh

# View recent logs
kubectl logs -n dinhanh -l app=django-web --tail=100
```

### Weekly
```bash
# Database backup
kubectl exec -n dinhanh deployment/postgres -- pg_dump -U dinhanh_user dinhanh_db > backup.sql

# Check resource usage
kubectl top nodes
kubectl top pods -n dinhanh
```

### Monthly
```bash
# Update dependencies
docker build -f Dockerfile.k8s -t registry/dinhanh:latest .
docker push registry/dinhanh:latest
kubectl set image deployment/django-web django=registry/dinhanh:latest -n dinhanh

# Security scan
trivy image registry/dinhanh:latest
```

## 🆘 Common Issues & Solutions

### 1. Pod stuck in CrashLoopBackOff
```bash
kubectl logs -n dinhanh POD_NAME --previous
kubectl describe pod -n dinhanh POD_NAME
```

### 2. PersistentVolume not mounting
```bash
kubectl get pvc -n dinhanh
kubectl describe pvc static-pvc -n dinhanh
```

### 3. Database connection error
```bash
# Test connectivity
kubectl exec -it deployment/django-web -n dinhanh -- python manage.py dbshell

# Check DNS
kubectl exec -it deployment/django-web -n dinhanh -- nslookup postgres
```

## 📚 Further Reading

- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)

## 💬 Support

For issues or questions, check:
1. Application logs: `kubectl logs -n dinhanh -f`
2. Kubernetes events: `kubectl describe pod -n dinhanh POD_NAME`
3. Docker Compose logs: `docker-compose logs -f`
