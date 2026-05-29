# 🚀 GitHub Actions - Complete Production Setup

Welcome! This directory contains all GitHub Actions workflows for your production-ready CI/CD pipeline.

## 📁 What's in This Directory?

```
.github/
├── workflows/                      # Workflow definitions
│   ├── ci-cd.yml                 # Main CI/CD pipeline
│   ├── code-quality.yml          # Code quality checks
│   ├── deploy-production.yml      # Production deployment
│   └── health-check.yml          # Production monitoring
│
├── README.md                       # This file
├── QUICK_REFERENCE.md             # Quick lookup guide (START HERE!)
├── GITHUB_ACTIONS_GUIDE.md        # Complete beginner guide
├── SETUP_CHECKLIST.md             # Setup verification
├── ARCHITECTURE.md                # System architecture diagrams
└── SETUP_SECRETS.md               # Vietnamese setup guide
```

## 🎯 Quick Start (5 minutes)

### 1. Add GitHub Secrets
```
Settings → Secrets and variables → Actions → New repository secret

Add:
- DOCKERHUB_USERNAME: your-username
- DOCKERHUB_TOKEN: your-personal-access-token
```

**Get token from:** https://hub.docker.com/settings/security

### 2. Test the Setup
```bash
git push origin main
# Go to Actions tab to watch it run!
```

### 3. Read the Guide
- **NEW TO GITHUB ACTIONS?** Start with: `QUICK_REFERENCE.md` (2 min)
- **WANT FULL EXPLANATION?** Read: `GITHUB_ACTIONS_GUIDE.md` (15 min)

## 📊 Your Workflows at a Glance

| Workflow | Triggers | Time | Purpose |
|----------|----------|------|---------|
| **CI/CD** | Push & PR | 15 min | Test, build, push Docker image |
| **Code Quality** | Push & PR | 5 min | Lint code, scan dependencies |
| **Deploy** | Manual/Release | 10 min | Deploy to production |
| **Health Check** | Every 6h | 2 min | Monitor production health |

## 🔄 What Happens When You Push Code?

```
git push → GitHub detects → Workflows run automatically

1. Tests run (Django, frontend)
2. Code quality checks run
3. If main branch: Docker build & push
4. Status shows in PR/commit
5. Merge when green ✅
```

## 🚀 How to Deploy

### Manual Deploy
1. Go to **Actions** tab
2. Click **Deploy to Production**
3. Click **Run workflow**
4. Choose environment
5. Click **Run workflow**

### Automatic Deploy (On Release)
1. Create release on GitHub
2. Tag version (e.g., `v1.0.0`)
3. Publish release
4. Deploy workflow runs automatically

## 🔐 Secrets You Need

### Minimum Required
```
DOCKERHUB_USERNAME      - Your Docker Hub username
DOCKERHUB_TOKEN         - Docker Hub Personal Access Token
```

### For Production Deploy (Add Later)
```
KUBECONFIG              - Kubernetes config (base64)
KUBE_NAMESPACE          - Kubernetes namespace
SLACK_WEBHOOK_URL       - For notifications (optional)
```

## 🎓 Learning Path

**Week 1:**
- Read `QUICK_REFERENCE.md`
- Add Docker Hub secrets
- Push code and watch workflows
- Understand each job

**Week 2:**
- Read `GITHUB_ACTIONS_GUIDE.md`
- Check workflow logs
- Learn YAML basics

**Week 3:**
- Troubleshoot failed workflows
- Test locally before pushing
- Understand error messages

**Week 4:**
- Deploy to production
- Set up branch protection
- Add Slack notifications

## 📚 Documentation

### For Beginners
- 📖 **QUICK_REFERENCE.md** - Quick lookup (2 min)
- 📖 **GITHUB_ACTIONS_GUIDE.md** - Complete guide (15 min)
- 📖 **SETUP_CHECKLIST.md** - Verification steps

### For Understanding the System
- 📊 **ARCHITECTURE.md** - Visual diagrams
- 🔧 **workflows/** - Actual workflow YAML files

### For Setup Help
- 🔐 **SETUP_SECRETS.md** - Vietnamese setup guide

## 🚨 If Something Goes Wrong

### Workflow Failed?
1. Click on failed workflow
2. Find the red ❌ job
3. Read the error message
4. Fix locally and push again

### Tests Failing?
```bash
# Test locally first
python manage.py test

# Build frontend locally
npm run build

# Build Docker image locally
docker build .
```

### Docker Push Failed?
- Check token not expired (Docker Hub)
- Check token has Write permissions
- Verify username is correct

## ✨ Features Included

- ✅ **Django Tests** - With PostgreSQL + Redis
- ✅ **Frontend Build** - Vite optimization
- ✅ **Docker Build** - Multi-stage optimization
- ✅ **Security Scanning** - Vulnerability detection
- ✅ **Code Quality** - Linting + formatting checks
- ✅ **Production Deploy** - Kubernetes deployment
- ✅ **Health Monitoring** - Automated health checks
- ✅ **Notifications** - Slack integration

## 🔗 Useful Links

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Hub Help](https://docs.docker.com/docker-hub/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Trivy Security Scanner](https://github.com/aquasecurity/trivy)

## 💡 Pro Tips

1. **Test locally before pushing** - Saves CI/CD time
2. **Write meaningful commits** - Helps identify changes
3. **Keep secrets secure** - Never commit passwords
4. **Monitor workflows** - Check Actions tab weekly
5. **Rotate tokens** - Every 6 months
6. **Skip CI for docs** - Add `[skip ci]` to commit
7. **Use branch protection** - Require tests to pass

## 🎯 Common Commands

### View Workflow Results
```
GitHub.com → Repository → Actions tab
```

### Trigger Workflow Manually
```
Actions tab → Choose workflow → Run workflow
```

### View Logs
```
Actions tab → Click run → Click job → Expand steps
```

### Skip CI for a Commit
```bash
git commit -m "Update docs [skip ci]"
```

## 📈 Performance

| Task | Time |
|------|------|
| PR checks | 15 min |
| Code quality | 5 min |
| Docker build | 10 min |
| Production deploy | 10 min |
| Health check | 2 min |

## 🎉 You're All Set!

Your production-grade GitHub Actions setup is complete and ready to use!

**Next steps:**
1. ✅ Add Docker Hub secrets (5 min)
2. ✅ Push code to test (2 min)
3. ✅ Read QUICK_REFERENCE.md (2 min)
4. ✅ Monitor first runs (10 min)

---

**Questions?** Check the documentation files above or search GitHub Actions docs.

**Need help?** Look at the error logs first - they usually explain the problem clearly!

---

**Status**: ✅ Production Ready
**Last Updated**: 2024
**Beginner Friendly**: Yes! ✨
