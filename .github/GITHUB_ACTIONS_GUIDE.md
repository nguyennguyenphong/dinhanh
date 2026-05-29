# GitHub Actions Production Setup - Complete Guide

**For Beginners**: This guide explains everything step-by-step. Don't worry if you're new to GitHub Actions!

---

## 📚 Table of Contents

1. [What is GitHub Actions?](#what-is-github-actions)
2. [Project Overview](#project-overview)
3. [Setup Instructions](#setup-instructions)
4. [Understanding the Workflows](#understanding-the-workflows)
5. [Common Tasks](#common-tasks)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## What is GitHub Actions?

GitHub Actions is a CI/CD (Continuous Integration/Continuous Deployment) tool built into GitHub.

**In simple terms:**
- Every time you push code, GitHub automatically runs tests
- If tests pass, it builds your Docker image
- If you release a version, it deploys to production
- You get notifications when things break

**Benefits:**
✅ Automated testing (catch bugs before production)
✅ Automated deployments (no manual pushing)
✅ Security scanning (find vulnerabilities)
✅ Free for public repositories
✅ No setup needed for basic runners

---

## Project Overview

This project uses **4 workflows**:

### 1. **CI/CD Pipeline** (`ci-cd.yml`)
- Tests Django code with PostgreSQL + Redis
- Builds frontend with Vite
- Scans for security vulnerabilities
- Builds Docker image
- Pushes to Docker Hub

**When it runs:** Every push and pull request

**Time:** ~15 minutes

### 2. **Code Quality** (`code-quality.yml`)
- Lints Python code (Black, Flake8)
- Lints JavaScript code (ESLint)
- Scans dependencies for vulnerabilities
- Validates Django migrations

**When it runs:** Every push and pull request

**Time:** ~5-10 minutes

### 3. **Production Deploy** (`deploy-production.yml`)
- Runs database migrations
- Deploys to Kubernetes cluster
- Runs health checks
- Sends notifications

**When it runs:** Manual trigger OR on release

**Time:** ~10 minutes

### 4. **Health Monitoring** (`health-check.yml`)
- Checks production is healthy
- Tests database connectivity
- Monitors pod status
- Alerts if problems found

**When it runs:** Every 6 hours (automatic)

**Time:** ~2 minutes

---

## Setup Instructions

### ✅ Step 1: Add GitHub Secrets

Secrets are secure variables that store sensitive data (passwords, tokens).

**Steps:**
1. Go to your GitHub repository
2. Click **Settings** (top menu)
3. In left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add each secret below:

#### Required Secrets:

```yaml
DOCKERHUB_USERNAME: your-docker-hub-username
DOCKERHUB_TOKEN: your-docker-hub-personal-access-token
```

**How to create Docker Hub token:**

1. Go to https://hub.docker.com/settings/security
2. Click **New Access Token**
3. Name: `github-actions`
4. Permissions: Check "Read", "Write", "Delete"
5. Click **Generate**
6. Copy the token and save to GitHub Secrets

#### Optional Secrets (for production deploy):

```yaml
KUBECONFIG: base64-encoded kubeconfig file
KUBE_NAMESPACE: your-kubernetes-namespace
DB_HOST: database-hostname
DB_USER: database-username
DB_NAME: database-name
DB_PASSWORD: database-password
SLACK_WEBHOOK_URL: slack-webhook-for-notifications
```

### ✅ Step 2: Verify Workflows are Present

Check that workflow files exist:

```bash
ls -la .github/workflows/
```

You should see:
- ✅ ci-cd.yml
- ✅ code-quality.yml
- ✅ deploy-production.yml
- ✅ health-check.yml

### ✅ Step 3: Test the Setup

Make a small change and push to see workflows run:

```bash
# Make a small change
echo "# Test" >> README.md

# Commit and push
git add .
git commit -m "Test: Trigger GitHub Actions"
git push origin main
```

**View the workflows:**
1. Go to your GitHub repository
2. Click **Actions** tab (top menu)
3. You should see a running workflow
4. Click it to see details

### ✅ Step 4: Configure Branch Protection (Optional but Recommended)

This ensures tests pass before merging:

1. Go to **Settings** → **Branches**
2. Click **Add rule**
3. Branch name pattern: `main`
4. Check: "Require status checks to pass before merging"
5. Check: "Require code review before merging"
6. Click **Create**

---

## Understanding the Workflows

### CI/CD Workflow (Runs on every push/PR)

```
┌─────────────────────────────────────┐
│  Your code push to GitHub           │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  Run Parallel Tests:                │
│  • Django Tests (5 min)            │
│  • Frontend Build (2 min)          │
│  • Code Quality (3 min)            │
└────────────┬────────────────────────┘
             ↓ (all pass?)
             ├─→ NO: Fail workflow, block merge
             ↓ YES
┌─────────────────────────────────────┐
│  Build Docker Image (on main only)  │
│  • Multi-stage build (5 min)       │
│  • Push to Docker Hub               │
│  • Add tags (latest, commit-hash)   │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  Security Scan                      │
│  • Trivy vulnerability scanner      │
│  • Upload results to GitHub         │
└─────────────────────────────────────┘
```

### How Each Test Works:

**Django Tests:**
- Creates temporary PostgreSQL database
- Creates temporary Redis server
- Runs migrations
- Runs test suite
- Cleans up

**Frontend Build:**
- Installs npm dependencies
- Runs Vite build
- Verifies `dist/` folder created

**Code Quality:**
- Checks code formatting (Black)
- Checks import sorting (isort)
- Runs linters (Flake8, ESLint)
- Scans dependencies (pip-audit, npm audit)

**Docker Build:**
- Multi-stage build (optimization)
- Frontend builder stage
- Python builder stage
- Final production stage
- Creates ~500MB image
- Pushes to Docker Hub

---

## Common Tasks

### How to Deploy to Production

**Option 1: Manual Deployment**

1. Go to **Actions** tab
2. Click **Deploy to Production** workflow
3. Click **Run workflow**
4. Choose environment (production/staging)
5. Enter image tag (optional, defaults to latest)
6. Click **Run workflow**
7. Monitor the logs

**Option 2: Automatic Deployment (On Release)**

1. Create a release on GitHub
2. Tag version (e.g., `v1.0.0`)
3. Add release notes
4. Click **Publish release**
5. Deploy workflow automatically triggers

### How to View Workflow Results

**View all runs:**
1. Go to **Actions** tab
2. See list of all workflow runs
3. Green checkmark = success
4. Red X = failure

**View specific workflow details:**
1. Click on workflow name in list
2. See each job and its status
3. Click job to expand and see logs
4. Click individual step to see full output

### How to Debug Failed Workflows

1. Click on the failed workflow run
2. Click on the failed job
3. Expand the failed step
4. Read the error message carefully
5. Fix the issue locally first
6. Test: `python manage.py test`, `npm run build`
7. Push fix to try again

### How to Skip CI for Certain Commits

Sometimes you just want to update docs without running tests:

```bash
git commit -m "Update README [skip ci]"
```

The workflow won't run.

### How to View Docker Images

```bash
# View images pushed to Docker Hub
docker pull yourusername/dinhanh:latest
docker images
```

---

## Troubleshooting

### Problem: Workflow shows "error"

**Steps to fix:**
1. Click the failed workflow
2. Look for the error message
3. Check if it's one of these common issues:
   - Tests failing locally? (Run `python manage.py test` locally first)
   - Missing secret? (Check Settings → Secrets)
   - Docker Hub login failed? (Check token not expired)
   - Port conflicts? (Usually temporary, try again)

### Problem: Docker push failed

**Checklist:**
- ✅ `DOCKERHUB_USERNAME` is set and correct?
- ✅ `DOCKERHUB_TOKEN` is set and correct?
- ✅ Token not expired? (Check Docker Hub)
- ✅ Token has "Write" permissions?
- ✅ Repo name correct? (Should match `IMAGE_NAME` env var)

**Fix:**
1. Go to Docker Hub settings
2. Check token expiration date
3. If expired, create new token
4. Update GitHub Secrets with new token

### Problem: Database test fails

**Checklist:**
- ✅ PostgreSQL service started?
- ✅ Correct credentials in test?
- ✅ `DB_NAME: dinhanh_test` in workflow?

**Check logs:**
- Look for "FAILED" in workflow logs
- Search for database error message
- Common: "could not connect to server"

**Solution:**
- Usually temporary networking issue
- Click **Re-run** button to retry

### Problem: Tests pass locally but fail in GitHub Actions

**Possible causes:**
- Different Python version (check workflow uses 3.11)
- Different environment variables
- Race conditions in tests (tests interfering with each other)
- Temporary file/port conflicts

**Fix:**
1. Match Python version locally: `python --version`
2. Export same env vars: `export DB_HOST=localhost`
3. Run tests in parallel: `python manage.py test --parallel`

---

## Best Practices

### 1. Always Test Locally First

Before pushing:

```bash
# Test Django
python manage.py test

# Test frontend build
npm run build

# Test Docker build
docker build .
```

### 2. Write Meaningful Commit Messages

✅ Good messages:
```
"Add user authentication API endpoint"
"Fix login form validation bug"
"Update dependencies to latest versions"
```

❌ Bad messages:
```
"Fix bug"
"Update stuff"
"Work in progress"
```

**Why?** Helps identify what changed in workflow logs and git history.

### 3. Keep Secrets Secure

❌ Never do this:
```bash
git commit -m "Add password: abc123" # DON'T!
echo "SECRET=value" > .env && git add .env # DON'T!
```

✅ Always do this:
```bash
# Use .gitignore to exclude secrets
echo ".env" >> .gitignore
git add .gitignore

# Use GitHub Secrets for sensitive data
# Add in Settings → Secrets
```

### 4. Monitor Workflows Regularly

- Check **Actions** tab weekly
- Review failed runs immediately
- Fix broken workflows before merging more code
- Keep logs for audit trail (GitHub keeps 30 days)

### 5. Use Branch Protection

- Require tests to pass before merge
- Require code review before merge
- This prevents broken code reaching main

**How to set up:**
1. Go to **Settings** → **Branches**
2. Click **Add rule**
3. Choose `main` branch
4. Check "Require status checks to pass"
5. Click **Create**

### 6. Optimize Workflow Speed

- Use `cache: 'pip'` and `cache: 'npm'` (already done)
- Run jobs in parallel when possible (already done)
- Skip CI for docs-only changes: `[skip ci]`
- Don't install unnecessary packages

### 7. Security Checklist

- ✅ Rotate Docker Hub token every 6 months
- ✅ Rotate Kubernetes credentials every 3 months
- ✅ Review GitHub Actions permissions regularly
- ✅ Don't commit secrets to git
- ✅ Use branch protection rules
- ✅ Monitor Action logs for suspicious activity

---

## Workflow Timing

### Expected run times:

| Workflow | Time | When |
|----------|------|------|
| PR checks | 15 min | Every PR |
| Code Quality | 5 min | Every push/PR |
| Docker Build | 10 min | Push to main |
| Deploy | 10 min | Manual/Release |
| Health Check | 2 min | Every 6 hours |

**Total from push to production:** ~30-40 minutes

---

## Helpful Links

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Hub Help](https://docs.docker.com/docker-hub/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Django Testing Guide](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Node.js Best Practices](https://nodejs.org/en/docs/guides/)

---

## Getting Help

1. **GitHub Actions logs** - Most detailed info available
2. **Search GitHub issues** - Others likely had same problem
3. **Stack Overflow** - Search with error message
4. **GitHub Discussions** - Ask community

---

**Questions?** Check the logs first - they usually explain the problem clearly!

Last Updated: 2024
