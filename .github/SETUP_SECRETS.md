# GitHub Actions - Setup Guide

## 📋 Required Secrets

Để sử dụng GitHub Actions CI/CD pipeline, bạn cần cấu hình các secrets sau:

### 1. Docker Hub Credentials

#### Bước 1: Tạo Docker Hub Personal Access Token
1. Đăng nhập vào [Docker Hub](https://hub.docker.com/)
2. Vào **Account Settings** → **Security** → **New Access Token**
3. Tạo token với tên: `github-actions`
4. Chọn quyền: `Read, Write, Delete`
5. Copy token (lưu ở nơi an toàn)

#### Bước 2: Thêm Secrets vào GitHub
1. Vào repository của bạn
2. Vào **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Thêm 2 secrets:
   - `DOCKERHUB_USERNAME`: Username Docker Hub của bạn
   - `DOCKERHUB_TOKEN`: Personal Access Token vừa tạo

## 🚀 CI/CD Pipeline Components

### 1. **Django Tests** (test-django job)
- Chạy trên mỗi push và pull request
- Tạo test database PostgreSQL
- Tạo Redis service
- Chạy migrations
- Chạy unit tests

**Cần thêm tests?** Bạn có thể tạo tests trong các Django apps bằng cách tạo `tests.py` hoặc thư mục `tests/`

### 2. **Frontend Build** (build-frontend job)
- Chạy trên mỗi push và pull request
- Cài đặt npm dependencies
- Build với Vite
- Verify `dist/` folder được tạo

### 3. **Docker Build & Push** (build-and-push job)
- Chỉ chạy khi push code lên `main` branch
- Build multi-stage Docker image (tối ưu kích thước)
- Tự động tag với:
  - `latest` (commit mới nhất trên main)
  - `main-{commit-sha}` (commit hash)
  - Branch name
- Push lên Docker Hub
- Cập nhật repository description

### 4. **Security Scan** (security-scan job)
- Chạy Trivy vulnerability scanner
- Scan file system tìm vulnerabilities
- Upload results vào GitHub Security tab

## 📊 Workflow Triggers

```yaml
# Pipeline chạy khi:
# 1. Push code lên main branch
# 2. Tạo Pull Request vào main branch

# Ngoại lệ:
# - Docker build & push CHỈ chạy khi push vào main (không chạy trên PR)
```

## 🔧 Customization

### Thay đổi nhánh trigger
Edit `.github/workflows/ci-cd.yml`:
```yaml
on:
  push:
    branches:
      - main          # ← Thay đổi ở đây
      - production    # ← Thêm nhánh khác nếu cần
```

### Thay đổi image name
Edit `.github/workflows/ci-cd.yml` env section:
```yaml
env:
  IMAGE_NAME: dinhanh  # ← Thay đổi ở đây
```

### Disable một job
Thêm `if: false` vào job:
```yaml
build-and-push:
  if: false  # Disable job này
```

## 📈 Monitoring

### Xem CI/CD runs
1. Vào repository
2. Click **Actions** tab
3. Xem danh sách các workflow runs
4. Click vào một run để xem chi tiết logs

### Troubleshooting

#### Docker Push Failed
- Kiểm tra `DOCKERHUB_USERNAME` và `DOCKERHUB_TOKEN` đúng không
- Token không hết hạn?
- Username tồn tại?

#### Tests Failed
- Kiểm tra logs trong GitHub Actions
- PostgreSQL/Redis service started?
- Environment variables correct?

#### Frontend Build Failed
- `npm ci` thành công?
- Tất cả dependencies cài đặt?
- `dist/` folder được tạo?

## 📝 Additional Setup (Optional)

### Automatic Deploy to Kubernetes
Nếu muốn auto-deploy, thêm job vào workflow:
```yaml
deploy-kubernetes:
  needs: [build-and-push]
  runs-on: ubuntu-latest
  steps:
    - name: Deploy to K8s
      run: |
        # Cấu hình kubeconfig
        # Chạy k8s-deploy.sh
```

### Slack Notifications
Thêm notification action:
```yaml
- name: Notify Slack
  uses: slackapi/slack-github-action@v1.24.0
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## 🎯 Best Practices

1. **Always test locally first**: Chạy `python manage.py test` và `npm run build` trước khi push
2. **Use meaningful commit messages**: Helps identify what changed in the workflow logs
3. **Monitor security alerts**: Check GitHub Security tab thường xuyên
4. **Keep token secret**: Không commit token hoặc secrets
5. **Regularly rotate tokens**: Regenerate access tokens mỗi 3-6 tháng

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Hub Personal Access Tokens](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Trivy Scanner](https://github.com/aquasecurity/trivy)
