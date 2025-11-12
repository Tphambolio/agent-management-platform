# Render Deployment Troubleshooting Guide

**Status**: CRITICAL - Deployment failing for 3+ hours
**Issue**: Database authentication failure
**Services**: wildfire-api-v2, wildfire-worker-v2

---

## Problem Summary

Both Render services have been failing to start due to PostgreSQL authentication errors:

```
FATAL: password authentication failed for user "postgres"
connection to server at "aws-1-us-east-1.pooler.supabase.com" (3.227.209.82), port 5432 failed
```

### Root Cause

The Supabase Session Pooler requires username format `postgres.PROJECT_ID` instead of just `postgres`.

**Required**: `postgres.ocwmvlamlxkfxohuzloh`
**Was using**: `postgres`

---

## Current Status

1. ✅ Added `SUPABASE_DB_USER` environment variable manually via Render dashboard
2. ✅ Triggered manual redeployment of both services
3. ⏳ Services currently deploying (showing 502 errors)
4. ❓ Need to verify deployment success once complete

---

## Environment Variables Configuration

### Required Variables (ALL FIVE must be set):

```
SUPABASE_URL=https://ocwmvlamlxkfxohuzloh.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=OmBuNzLSxggeXtfA5ZRkqp0CWzvPyQG+bnCLHpZ3d/BvA30A7QVdYa92SxbnbuPSJt5lwUFkeZPzVJGihQrcXA==
SUPABASE_DB_PASSWORD=lMNGAwACJTeG1E83
```

### Database Connection Variables:

```
SUPABASE_DB_HOST=aws-1-us-east-1.pooler.supabase.com
SUPABASE_DB_PORT=5432
SUPABASE_DB_USER=postgres.ocwmvlamlxkfxohuzloh  ← CRITICAL!
```

---

## Verification Steps

### 1. Check Environment Variables

Visit both services in Render dashboard and verify `SUPABASE_DB_USER` is set:

- API: https://dashboard.render.com/web/srv-d44n8hn5r7bs73b1dvp0/environment
- Worker: https://dashboard.render.com/worker/srv-d44n8hn5r7bs73b1dvpg/environment

### 2. Check Deployment Logs

Look for these success messages:
```
Database config: host=aws-1-us-east-1.pooler.supabase.com, port=5432, user=postgres.ocwmvlamlxkfxohuzloh
Pooler detected: True
Database connection established
```

### 3. Test Health Endpoint

Once deployment shows "Live" status:
```bash
curl https://wildfire-api-v2.onrender.com/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "2.0.0"
}
```

---

## Code Changes Made

### File: `backend/config_supabase.py`

1. **Fixed dataclass field ordering** (line 27-35):
   - Moved `api_url` before default fields to fix TypeError

2. **Added username auto-detection** (line 96-98):
   ```python
   default_user = f'postgres.{project_id}' if 'pooler' in db_host else 'postgres'
   db_user = os.getenv('SUPABASE_DB_USER', default_user)
   ```

3. **Added debug logging** (line 100-105):
   ```python
   logger.info(f"Database config: host={db_host}, port={db_port}, user={db_user}")
   logger.info(f"Pooler detected: {'pooler' in db_host}, default_user={default_user}")
   ```

### File: `backend/app.py`

- **Fixed Gunicorn WSGI** (line 214):
  ```python
  app = create_app()  # Module-level instance for WSGI servers
  ```

### File: `render.yaml`

- **Updated startCommand** (line 13):
  ```yaml
  startCommand: gunicorn ... backend.app:app  # Changed from backend.app:create_app
  ```

---

## Timeline of Actions

1. **03:30 - Initial deployment** - Failed with IPv6 error
2. **04:00 - Switched to Session Pooler** - Changed to IPv4-compatible pooler
3. **05:00 - Fixed username format** - Auto-detection code added
4. **05:30 - Manual env var addition** - Added SUPABASE_DB_USER via dashboard
5. **06:00 - Redeployment triggered** - Both services redeploying
6. **06:10+ - Current status** - Waiting for deployment to complete

---

## If Deployment Fails Again

### Checklist:

1. **Verify SUPABASE_DB_USER is set** in both services
2. **Check deployment logs** for the debug logging output
3. **Test database connection locally**:
   ```python
   import psycopg2
   conn = psycopg2.connect(
       host="aws-1-us-east-1.pooler.supabase.com",
       port=5432,
       database="postgres",
       user="postgres.ocwmvlamlxkfxohuzloh",
       password="lMNGAwACJTeG1E83"
   )
   ```
4. **Verify Supabase project is active** (not paused)
5. **Check for typos** in environment variable names

### Alternative Approaches:

1. **Use direct connection** instead of pooler (requires IPv6 support - won't work on Render)
2. **Switch to different deployment platform** (Fly.io, Railway, etc.)
3. **Deploy database separately** (not using Supabase pooler)

---

## Success Criteria

- ✅ Both services show "Live" status in Render dashboard
- ✅ Health endpoint returns `"status": "healthy"`
- ✅ No authentication errors in logs
- ✅ Can create test user via API
- ✅ Worker process starts without errors

---

## Contact & Resources

- **Render Dashboard**: https://dashboard.render.com
- **Supabase Dashboard**: https://supabase.com/dashboard/project/ocwmvlamlxkfxohuzloh
- **Deployment logs**: Available in Render dashboard under "Logs" tab
- **Environment setup guide**: `RENDER_ENV_SETUP.md`

---

**Last Updated**: 2025-11-04 06:15 UTC
**Status**: Awaiting deployment completion (estimated 5-10 minutes from 06:10)
