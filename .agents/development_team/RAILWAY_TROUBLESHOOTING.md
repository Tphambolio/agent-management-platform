# 🔧 Railway Deployment Troubleshooting Guide

**Last Updated**: 2025-10-27
**Status**: Active troubleshooting for CrisisKit backend deployment

This guide covers common Railway deployment issues and their solutions, organized by symptom.

---

## 🚨 Symptom-Based Troubleshooting

### Issue 1: "Invalid value for '--port': '$PORT' is not a valid integer"

**Symptom**:
```
Error: Invalid value for '--port': '$PORT' is not a valid integer.
Container failed to start
```

**Root Cause**:
The `PORT` environment variable is not being expanded before being passed to the application.

**Solutions** (try in order):

#### Solution A: Fix Dockerfile CMD (Most Common)

Check your `Dockerfile`:

```dockerfile
# ❌ WRONG - Exec form doesn't expand variables
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "$PORT"]

# ✅ CORRECT - Shell form expands variables
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
```

**How to fix**:
1. Edit `Dockerfile`
2. Change CMD line to shell form (no brackets, no quotes)
3. Use `${PORT:-8000}` syntax (falls back to 8000 if PORT not set)
4. Commit and push

#### Solution B: Fix railway.json Builder

Check your `railway.json`:

```json
{
  "build": {
    "builder": "DOCKERFILE",  // ← Must be DOCKERFILE, not NIXPACKS
    "dockerfilePath": "Dockerfile"
  }
}
```

**Why this matters**:
- If `builder` is set to `"NIXPACKS"`, Railway ignores your Dockerfile completely
- NIXPACKS has its own rules for environment variables
- You MUST use `"DOCKERFILE"` builder to use your custom Dockerfile

**How to fix**:
1. Edit `railway.json`
2. Change `"builder": "NIXPACKS"` to `"builder": "DOCKERFILE"`
3. Remove any `startCommand` overrides
4. Commit and push

#### Solution C: Remove startCommand Override

Check `railway.json` for this:

```json
{
  "deploy": {
    "startCommand": "uvicorn app:app --host 0.0.0.0 --port $PORT"  // ← REMOVE THIS
  }
}
```

**Problem**: `startCommand` in railway.json overrides your Dockerfile CMD, and it doesn't expand variables properly.

**How to fix**:
1. Remove the entire `startCommand` line from railway.json
2. Let Dockerfile CMD handle startup
3. Commit and push

#### Solution D: Use Railway Environment Variable

If nothing else works, set PORT explicitly:

1. Go to Railway Dashboard → Your Service → Variables
2. Add: `PORT = 8000`
3. Redeploy

**Note**: Railway usually auto-injects PORT, so this is a last resort.

---

### Issue 2: Backend Returns 502 Bad Gateway

**Symptom**:
```bash
curl https://your-app.up.railway.app/health
# Returns: 502 Bad Gateway
```

**Root Causes & Solutions**:

#### Cause A: Application Not Starting

**Check logs**:
```bash
railway logs --follow
# Look for Python errors, import failures, or crashes
```

**Common problems**:
- Missing dependencies in `requirements.txt`
- Python syntax errors
- Missing files (check Dockerfile COPY commands)
- Database connection failure (see Issue 3)

**Solution**:
1. Fix the error shown in logs
2. Redeploy

#### Cause B: Health Check Failing

**Check railway.json**:
```json
{
  "deploy": {
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300  // ← Increase if health check is slow
  }
}
```

**Symptoms**:
- Logs show app starting successfully
- But Railway keeps restarting the container
- "Health check failed" messages

**Solutions**:
1. Test health endpoint locally:
   ```bash
   curl http://localhost:8000/health
   ```
2. If slow, increase `healthcheckTimeout` to 300-600 seconds
3. Check health endpoint doesn't require database (can cause circular dependency)
4. Verify health endpoint returns 200 status code

#### Cause C: Wrong Port

**Check logs for**:
```
INFO: Uvicorn running on http://0.0.0.0:8000
```

**Problem**: If Railway assigned PORT=8001 but app listens on 8000, health check fails.

**Solution**:
- Use `${PORT:-8000}` in Dockerfile CMD (see Issue 1)
- Verify logs show: `Uvicorn running on http://0.0.0.0:[PORT from Railway]`

#### Cause D: Database Not Connected

See Issue 3 below.

---

### Issue 3: Database Connection Errors

**Symptom**:
```
psycopg2.OperationalError: could not connect to server
FATAL: password authentication failed
connection refused
```

**Root Cause**: No PostgreSQL database OR wrong DATABASE_URL.

#### Solution A: Add PostgreSQL Database

**You must manually add PostgreSQL to your Railway project.**

See: `.agents/RAILWAY_POSTGRESQL_SETUP.md` for step-by-step guide.

Quick steps:
1. Railway Dashboard → Your Project
2. Click "New" → "Database" → "Add PostgreSQL"
3. Wait for provisioning (30-60 seconds)
4. Verify `DATABASE_URL` appears in your app's Variables tab
5. Redeploy

#### Solution B: Verify DATABASE_URL Format

**Correct format**:
```
DATABASE_URL=postgresql://user:password@hostname:5432/database
```

**Check in Railway**:
1. Your Service → Variables tab
2. Look for `DATABASE_URL`
3. Should start with `postgresql://`

**If missing**:
1. Click on Postgres service
2. Go to "Connect" tab
3. Copy "Database URL"
4. Manually add to your app's Variables tab

#### Solution C: Check PostgreSQL Service Status

1. Railway Dashboard → Your Project
2. Find "Postgres" service box
3. Status should be **"Active"** (green indicator)

**If status is "Failed" or "Crashed"**:
- Delete the Postgres service
- Re-add it (see RAILWAY_POSTGRESQL_SETUP.md)
- Check your Railway plan (Hobby includes Postgres)

#### Solution D: Use SQLite Fallback (Temporary)

**⚠️ WARNING**: SQLite on Railway loses data on every restart!

If you can't get Postgres working, temporarily use SQLite:

1. Railway Dashboard → Your Service → Variables
2. **Delete** the `DATABASE_URL` variable
3. Redeploy

Your app will fall back to SQLite mode.

**To restore Postgres later**:
1. Re-add PostgreSQL database (see RAILWAY_POSTGRESQL_SETUP.md)
2. `DATABASE_URL` will auto-appear
3. Redeploy

---

### Issue 4: Build Failures

**Symptom**:
```
Build failed
ERROR: Could not install packages
ModuleNotFoundError
```

#### Cause A: Missing Dependencies

**Solution**:
1. Check `requirements.txt` includes all packages
2. For CrisisKit, must include:
   ```
   fastapi
   uvicorn
   psycopg2-binary
   pillow
   openai
   # ... etc
   ```
3. Commit and push

#### Cause B: Incompatible Python Version

**Check Dockerfile**:
```dockerfile
FROM python:3.11-slim  # ← Should be 3.11 or 3.10
```

**Railway uses**:
- Python 3.11 by default (if no Dockerfile)
- Whatever you specify in Dockerfile

**Solution**:
- Keep Python version consistent between local dev and Dockerfile

#### Cause C: System Dependencies Missing

**For CrisisKit (needs WeasyPrint)**:

```dockerfile
# Must have these for PDF generation
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*
```

**Symptom if missing**:
```
OSError: cannot load library 'gobject-2.0-0'
ImportError: libpango
```

**Solution**:
- Add system dependencies to Dockerfile RUN command
- Rebuild

---

### Issue 5: Application Crashes on Startup

**Symptom**:
```
Container exited with code 1
Application startup failed
```

**Check logs for**:

#### Error A: Import Errors

```
ModuleNotFoundError: No module named 'fastapi'
ImportError: cannot import name 'FastAPI'
```

**Solution**:
- Add missing package to `requirements.txt`
- Verify package name spelling

#### Error B: File Not Found

```
FileNotFoundError: [Errno 2] No such file or directory: 'app.py'
```

**Solution**:
- Check Dockerfile COPY commands include all required files
- For CrisisKit:
  ```dockerfile
  COPY app.py .
  COPY forms.py .
  COPY mapping.py .
  COPY infrastructure.py .
  # ... etc
  ```

#### Error C: Database Initialization Failure

```
sqlite3.OperationalError: unable to open database file
```

**Solution**:
- Ensure Dockerfile creates data directory:
  ```dockerfile
  RUN mkdir -p /app/data
  ```
- OR: Switch to PostgreSQL (recommended)

---

### Issue 6: "Service Unavailable" (503)

**Symptom**:
- 502 Bad Gateway → Application is crashing
- 503 Service Unavailable → Application is starting/restarting

**If 503 persists**:

1. **Check restart loop**:
   ```bash
   railway logs --follow
   # Look for repeated "Container started" → "Container exited" cycles
   ```

2. **Check restart policy** in railway.json:
   ```json
   {
     "deploy": {
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10  // ← Increase to 10-15
     }
   }
   ```

3. **Increase health check timeout**:
   ```json
   {
     "deploy": {
       "healthcheckTimeout": 300  // ← 5 minutes
     }
   }
   ```

---

### Issue 7: Environment Variables Not Loading

**Symptom**:
```python
os.getenv("DATABASE_URL")  # Returns None
```

**Solutions**:

#### Solution A: Verify Variable Exists

1. Railway Dashboard → Your Service → Variables tab
2. Check variable is listed
3. Check spelling (case-sensitive!)

#### Solution B: Redeploy After Adding

**Important**: Variables are only injected on NEW deployments.

After adding a variable:
1. Go to Deployments tab
2. Click "Redeploy" on latest deployment
3. OR: Push a new commit

#### Solution C: Check Variable Scope

Some Railway projects have multiple environments:
- Production
- Preview
- Development

**Solution**:
1. Make sure variable is added to **Production** environment
2. Or: Add to "All environments"

---

### Issue 8: Slow Build Times

**Symptom**:
- Build takes 5-10+ minutes
- Repeatedly downloads same packages

**Solutions**:

#### Solution A: Use Layer Caching

```dockerfile
# ✅ GOOD - Copy requirements first, then code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY forms.py .
# ... rest of files
```

```dockerfile
# ❌ BAD - Changes to any file rebuild everything
COPY . .
RUN pip install -r requirements.txt
```

**Why**: Docker caches layers. If requirements.txt doesn't change, pip install layer is reused.

#### Solution B: Use Smaller Base Image

```dockerfile
# ✅ Faster: python:3.11-slim (200 MB)
FROM python:3.11-slim

# ❌ Slower: python:3.11 (1 GB)
FROM python:3.11
```

#### Solution C: Remove Unnecessary Files

Create `.dockerignore`:
```
.git
.pytest_cache
__pycache__
*.pyc
.env
.venv
node_modules
tests/
.agents/
docs/
knowledge_base/
```

**Why**: Speeds up COPY commands by excluding unnecessary files.

---

## 🔍 Diagnostic Commands

### Check Service Status

```bash
railway status
```

**Expected output**:
```
Service: crisiskit-backend
Status: Active
URL: https://crisiskit-production.up.railway.app
```

### View Real-Time Logs

```bash
railway logs --follow
```

**Look for**:
- ✅ `INFO: Uvicorn running on http://0.0.0.0:[PORT]`
- ✅ `INFO: Application startup complete`
- ✅ `Using PostgreSQL connection pool`
- ❌ Any ERROR or FATAL messages
- ❌ Repeated container restarts

### Test Health Endpoint

```bash
curl https://your-app.up.railway.app/health

# Expected response:
{
  "status": "ok",
  "service": "crisiskit-api",
  "checks": {
    "database": {"status": "healthy"}
  }
}
```

### Check Environment Variables

```bash
railway variables

# Or in Railway Dashboard:
# Your Service → Variables tab
```

**Must have**:
- `PORT` (auto-injected by Railway)
- `DATABASE_URL` (if using Postgres)

### Manually Trigger Deployment

```bash
# Redeploy current code
railway redeploy

# Deploy local changes
railway up
```

---

## 📋 Pre-Deployment Checklist

Before deploying to Railway, verify:

- [ ] `railway.json` uses `"builder": "DOCKERFILE"`
- [ ] `Dockerfile` CMD uses shell form: `CMD uvicorn app:app ...`
- [ ] `Dockerfile` uses `${PORT:-8000}` for port
- [ ] `requirements.txt` includes all dependencies
- [ ] `requirements.txt` includes `psycopg2-binary` for Postgres
- [ ] PostgreSQL database added to Railway project
- [ ] `DATABASE_URL` variable exists in service
- [ ] Health check endpoint (`/health`) works locally
- [ ] App starts successfully with `uvicorn app:app --reload`

---

## 🆘 Emergency Procedures

### Rollback to Last Working Deployment

1. Railway Dashboard → Your Service → Deployments
2. Find last successful deployment
3. Click "..." menu → "Redeploy"

### Switch to SQLite Temporarily

1. Railway Dashboard → Your Service → Variables
2. Delete `DATABASE_URL` variable
3. Redeploy

**⚠️ WARNING**: All data will be lost on next restart!

### Check Railway Status

If nothing works, check Railway platform status:
- https://railway.app/status

Look for:
- Ongoing incidents
- Degraded performance
- Region-specific issues

---

## 📞 Getting Further Help

If you've tried everything:

1. **Gather diagnostics**:
   ```bash
   railway logs > railway_logs.txt
   railway status > railway_status.txt
   railway variables > railway_vars.txt
   ```

2. **Check Railway docs**:
   - https://docs.railway.app
   - https://docs.railway.app/deploy/deployments
   - https://docs.railway.app/databases/postgresql

3. **Railway Discord**:
   - https://discord.gg/railway

4. **Railway Support**:
   - https://railway.app/help

---

## 🔗 Related Docs

- `.agents/RAILWAY_POSTGRESQL_SETUP.md` - PostgreSQL setup guide
- `.agents/RAILWAY_CLI_COMMANDS.sh` - Useful CLI commands
- `.agents/reports/railway-debug-report.json` - Technical analysis
- `railway.json` - Railway configuration
- `Dockerfile` - Container configuration

---

## 📊 Success Indicators

Your deployment is working when you see:

**In Logs**:
```
✓ Build succeeded
✓ Starting Container
✓ INFO: Using PostgreSQL connection pool (Railway production mode)
✓ INFO: Started server process [1]
✓ INFO: Uvicorn running on http://0.0.0.0:8000
✓ INFO: Application startup complete
```

**In Dashboard**:
- Service status: **Active** (green)
- Latest deployment: **Success**
- Health check: **Passing**

**Via Curl**:
```bash
curl https://your-app.up.railway.app/health
# {"status":"ok","service":"crisiskit-api","checks":{"database":{"status":"healthy"}}}
```

**If ALL these are true** → You're live! 🎉
