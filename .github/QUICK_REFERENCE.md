# GitHub Actions - Quick Reference

## 🚀 Quick Commands

### View All Workflows
```bash
# In GitHub UI:
# 1. Go to Actions tab
# 2. See list on left side
```

### Trigger a Workflow Manually
```bash
# 1. Go to Actions tab
# 2. Click workflow name
# 3. Click "Run workflow"
# 4. Choose branch
# 5. Click "Run workflow"
```

### Restart Failed Workflow
```bash
# 1. Go to Actions tab
# 2. Click failed workflow run
# 3. Click "Re-run failed jobs"
```

### View Workflow Logs
```bash
# 1. Actions tab → Click workflow run
# 2. Click job name to expand
# 3. Click step name to see full output
```

---

## 📋 Workflow Quick Start

### When you PUSH code to main:

1. **CI/CD runs** (15 min)
   - Tests Django
   - Builds frontend
   - Builds Docker image
   - Pushes to Docker Hub

2. **Status shows in PR**
   - Green ✅ = All passed
   - Red ❌ = Something failed
   - Yellow ⏳ = Still running

3. **Check Actions tab to see details**

---

## 🐛 Common Fixes

### Tests Failed Locally?
```bash
# Run tests before pushing
python manage.py test

# Check specific app
python manage.py test accounts

# Run with verbose output
python manage.py test --verbosity=2

# Run parallel tests
python manage.py test --parallel
```

### Frontend Build Failed?
```bash
# Build locally first
npm run build

# Check dist folder created
ls -la dist/

# Clean install if cached issues
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Docker Build Failed?
```bash
# Build Docker image locally
docker build -t dinhanh:test .

# Check Dockerfile syntax
docker build --dry-run .
```

### GitHub Action Secrets Issues?
```bash
# Add new secret:
# 1. Settings → Secrets and variables → Actions
# 2. Click "New repository secret"
# 3. Name: YOUR_SECRET_NAME
# 4. Value: your-secret-value
# 5. Click "Add secret"

# Update existing secret:
# 1. Click secret name
# 2. Click "Update"
# 3. Paste new value
```

---

## ✅ Pre-Push Checklist

Before pushing to main:

```bash
# 1. Run tests
python manage.py test

# 2. Check code formatting
black --check .

# 3. Build frontend
npm run build

# 4. Build Docker image (optional)
docker build .

# 5. Create meaningful commit message
git commit -m "Feature: Add new API endpoint"

# 6. Push
git push origin main
```

---

## 📊 Workflow Status Icons

| Icon | Meaning | Next Step |
|------|---------|-----------|
| ✅ | Passed | Deploy if ready |
| ❌ | Failed | Check logs, fix code, push again |
| ⏳ | Running | Wait for completion |
| ⊘ | Skipped | Expected (e.g., `[skip ci]`) |

---

## 🔑 Secrets Needed

### Minimum (Docker push):
```
DOCKERHUB_USERNAME: your-username
DOCKERHUB_TOKEN: your-token
```

### For Production Deploy:
```
KUBECONFIG: your-kubeconfig (base64)
KUBE_NAMESPACE: your-namespace
SLACK_WEBHOOK_URL: your-webhook (optional)
```

---

## 🚨 Emergency: Disable Workflow

If workflow is broken and blocking everything:

1. Go to `.github/workflows/FILENAME.yml`
2. Add at top of file:
```yaml
on:
  workflow_dispatch:  # Keep this
  # Comment out triggers temporarily:
  # push:
  #   branches: [main]
  # pull_request:
  #   branches: [main]
```
3. Save and push
4. Workflow won't run until you re-enable it

---

## 📞 Need Help?

1. **Check the logs** - Click workflow → job → step
2. **Read error message** - Usually explains the problem
3. **Search GitHub issues** - Others likely had same issue
4. **Ask in GitHub Discussions** - Community can help

---

## ⏱️ Typical Times

| Task | Time |
|------|------|
| Run tests | 5-7 min |
| Build frontend | 2-3 min |
| Code quality | 2-3 min |
| Build Docker | 5-10 min |
| Deploy | 10 min |
| Health check | 2 min |

---

## 💡 Pro Tips

1. **Use branch protection** - Require tests to pass before merge
2. **Use meaningful commits** - Helps identify changes in logs
3. **Test locally first** - Save CI/CD time
4. **Watch the Actions tab** - Stay on top of issues
5. **Rotate secrets** - Every 6 months for tokens
6. **Skip CI for docs** - Add `[skip ci]` to commit message
7. **Save logs** - GitHub keeps 30 days, useful for audit trail

---

## 🔗 Links

- [Full GitHub Actions Guide](./.github/GITHUB_ACTIONS_GUIDE.md)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Hub Docs](https://docs.docker.com/docker-hub/)

---

**Last Updated**: 2024
**Difficulty**: Beginner Friendly ✨
