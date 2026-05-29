# Helm Chart for Dinhanh Application

## Install Helm Chart

```bash
# Add repository
helm repo add dinhanh ./chart
helm repo update

# Install
helm install dinhanh ./chart/dinhanh -n dinhanh --create-namespace -f values-prod.yaml

# Upgrade
helm upgrade dinhanh ./chart/dinhanh -n dinhanh -f values-prod.yaml

# Uninstall
helm uninstall dinhanh -n dinhanh
```

## Chart Structure

```
dinhanh/
├── Chart.yaml
├── values.yaml
├── values-prod.yaml
├── templates/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── postgres.yaml
│   ├── redis.yaml
│   ├── django-web-deployment.yaml
│   ├── django-web-service.yaml
│   ├── django-web-hpa.yaml
│   ├── celery-worker-deployment.yaml
│   ├── celery-beat-deployment.yaml
│   ├── ingress.yaml
│   ├── pdb.yaml
│   └── _helpers.tpl
```
