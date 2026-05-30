# GitHub Actions — CI/CD Documentation

This document describes the automated pipelines that guard the **Dinhanh** project (Django 6.0.5 + PostgreSQL + Node.js 20).

---

## Workflow Overview

| File | Trigger | Purpose |
|------|---------|---------|
| `ci-cd.yml` | Push / PR → `main` | Run tests, build frontend, push Docker image |
| `code-quality.yml` | Push / PR → `main`, `develop` | Lint, format, dependency audit, Django checks |
| `deploy-production.yml` | Manual dispatch / GitHub Release | Database migration → K8s deploy → health check → auto-rollback |
| `health-check.yml` | Scheduled (every 6 h) + manual | Monitor pods, endpoints, database, error rate |

---

## Secrets Required

All secrets are configured in **Settings → Secrets and variables → Actions**.

### Docker Hub

| Secret | Description |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Docker Hub account username |
| `DOCKERHUB_TOKEN` | Docker Hub access token (not your password) |

### Kubernetes

| Secret | Description |
|--------|-------------|
| `KUBECONFIG` | Full kubeconfig file, **base64-encoded** (`base64 -w0 ~/.kube/config`) |
| `KUBE_NAMESPACE` | Kubernetes namespace where the app runs (e.g. `dinhanh-prod`) |

### Database (used by health-check monitoring only)

| Secret | Description |
|--------|-------------|
| `DB_HOST` | PostgreSQL host (in-cluster service name or external IP) |
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_NAME` | PostgreSQL database name |

### Notifications (optional)

| Secret | Description |
|--------|-------------|
| `SLACK_WEBHOOK_URL` | Incoming Webhook URL for deployment and alert notifications |

---

## Workflow Details

### 1. `ci-cd.yml` — Production CI/CD Pipeline

**Jobs (in order):**

```
test-django ──┬── build-and-push
build-frontend─┤
security-scan ─┘
               └── notify
```

- **test-django** — Spins up PostgreSQL 16 + Redis 7, runs `pytest` with coverage (minimum 70 %). Fails the pipeline if coverage drops below threshold.
- **build-frontend** — Installs npm dependencies and runs `npm run build`. Uploads the `dist/` folder as an artifact for the Docker build step.
- **security-scan** — Trivy filesystem scan. Fails on **CRITICAL** CVEs; results are uploaded to the GitHub Security tab.
- **build-and-push** — Runs only on push to `main`. Downloads the `dist/` artifact, builds the Docker image, and pushes it to Docker Hub with multi-tag support (`latest`, branch name, short SHA, semver). Also generates SBOM and provenance attestations.

**Docker image tags produced:**

| Tag | Example |
|-----|---------|
| `latest` | Always points to the newest main build |
| `main` | Branch name |
| `main-<sha>` | Short commit SHA, e.g. `main-a1b2c3d` |
| `1.2.3` | From Git semver tag |
| `1.2` | Major.minor from Git semver tag |

---

### 2. `code-quality.yml` — Code Quality & Linting

Runs in parallel across four jobs — **all must pass** for the pipeline to be green.

| Job | Tools | Behaviour |
|-----|-------|-----------|
| `python-lint` | Black, isort, Flake8 | Hard fail — no `\|\| true` |
| `javascript-lint` | ESLint, Prettier | Hard fail if the scripts exist in `package.json`; skips gracefully if not installed |
| `dependency-check` | pip-audit, npm audit | Fails on any HIGH/CRITICAL Python CVE; fails on moderate+ npm vulnerability |
| `django-checks` | `manage.py check`, `makemigrations --check` | Fails if any Django system check fails or if a model change lacks a migration file |

> **Tip:** Add `[skip ci]` to a commit message to bypass these checks temporarily.

---

### 3. `deploy-production.yml` — Deploy to Production

**Trigger options:**

1. **Manual dispatch** (`workflow_dispatch`) — choose environment (`production` or `staging`) and image tag.
2. **GitHub Release published** — automatically deploys the release.

**Job flow:**

```
pre-deployment-checks
        │
database-migration          ← runs python manage.py migrate in a K8s Job
        │
deploy-kubernetes           ← kubectl set image + rollout status
        │
post-deployment-tests       ← curl /health/ via port-forward (6 retries × 5 s)
        │
rollback-on-failure (if any above job fails)
        │
notify-deployment (always)
```

**Rollback mechanism:**  
Before updating the deployment image, the current image digest is saved as a job output. If either `deploy-kubernetes` or `post-deployment-tests` fails, the `rollback-on-failure` job automatically re-pins the deployment to the previous image.

**Kubernetes annotation** (replaces deprecated `--record`):
```
kubernetes.io/change-cause: "GitHub Actions deploy: <sha> by <actor>"
```
Use `kubectl rollout history deployment/dinhanh` to view this history.

---

### 4. `health-check.yml` — Scheduled Monitoring

Runs automatically **every 6 hours** (00:00, 06:00, 12:00, 18:00 UTC). Can also be triggered manually.

**Checks performed:**

| Check | Pass condition |
|-------|----------------|
| Deployment readiness | `Available` condition is `True` |
| Pod count | At least 1 pod in `Running` phase |
| Resource usage | `kubectl top` (informational; no fail if metrics-server is absent) |
| `/health/` endpoint | HTTP 200 within 30 s (6 retries) |
| `/api/` endpoint | HTTP 200 (warning only) |
| Error rate in logs | < 20 ERROR/CRITICAL lines in last 200 log lines (warning only; Slack alert sent) |
| Database connectivity | `psql SELECT version()` via a temporary pod |

If any check fails, a Slack alert is sent automatically (requires `SLACK_WEBHOOK_URL` secret).

---

## Python & Runtime Versions

| Component | Version |
|-----------|---------|
| Django | 6.0.5 |
| Python | 3.12 (minimum required by Django 6) |
| PostgreSQL | 16 |
| Node.js | 20 LTS |
| kubectl | v1.29.0 |

> Django 6.0 dropped support for Python 3.11 and below. Always use Python 3.12+.

---

## Local Pre-commit Checks

Run the same checks locally before pushing:

```bash
# Python formatting
black .
isort . --profile black

# Python lint
flake8 . --exclude=venv/,migrations/ --ignore=E501,W503 --max-line-length=100

# Check for missing migrations
python manage.py makemigrations --check --dry-run

# Run tests with coverage
pytest --ds=dinhanh.settings --cov=. --cov-report=term-missing

# Frontend
npm run lint
npm run format:check
npm run build
```

---

## Adding a New Environment Variable

1. Add the secret in **Settings → Secrets and variables → Actions**.
2. Reference it in the relevant workflow with `${{ secrets.YOUR_SECRET_NAME }}`.
3. Add it to the `dinhanh-secrets` Kubernetes Secret so that in-cluster jobs can access it.

---

## Troubleshooting

### Migration job fails
Check logs: `kubectl logs -l component=migration -n <namespace> --tail=100`

### Docker push fails with `unauthorized`
Verify `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` are still valid (tokens expire).

### Health check cannot reach `/health/`
Ensure the `dinhanh` Kubernetes Service is exposing port `8000` and the Django `ALLOWED_HOSTS` includes the cluster internal hostname.

### `kubectl wait` times out
The deployment may be stuck in a pending state. Check: `kubectl describe deployment dinhanh -n <namespace>` and `kubectl get events -n <namespace> --sort-by=.lastTimestamp`.