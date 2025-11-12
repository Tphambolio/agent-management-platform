# 🚂 Railway PostgreSQL Setup Guide - Step by Step

**Status**: Your backend is returning 502 because it needs a PostgreSQL database
**Goal**: Add PostgreSQL to your Railway project so the backend can start
**Time**: 5-10 minutes

---

## 🎯 Quick Check First

Before we start, verify you're in the right place:

1. Go to: **https://railway.app/dashboard**
2. You should see a list of your projects
3. Find the project named **"CrisisKit"** or similar (whatever you named it)
4. Click on it

**What you should see**:
- A project page with your services listed
- At least ONE service (your backend Python app)
- Maybe a "Postgres" service already (if you added it)

---

## Method 1: Add PostgreSQL via Railway Dashboard (RECOMMENDED)

### Step 1: Open Your Project

1. Go to: **https://railway.app/dashboard**
2. Click on your **CrisisKit project** (or whatever it's named)
3. You'll see a canvas/workspace with boxes representing services

**What you're looking for**:
- Your main app service (probably named "crisiskit", "web", or has your repo name)
- An empty canvas area where you can add more services

---

### Step 2: Add New Database Service

**Look for ONE of these options** (Railway UI changes, so try in order):

#### Option A: "New" Button (Top Right)
1. Look in the **top-right corner** of the project page
2. Click the **"New"** button (or "+ New")
3. A dropdown appears with options like:
   - Service
   - Database ← **SELECT THIS**
   - Empty Service
   - etc.
4. Click **"Database"**
5. You'll see database options: PostgreSQL, MySQL, Redis, MongoDB
6. Click **"Add PostgreSQL"** (or "PostgreSQL")

#### Option B: "+" Button in Canvas
1. Look for a **"+"** button floating in the canvas area
2. Click it
3. Select **"Database"** from the menu
4. Choose **"PostgreSQL"**

#### Option C: Right-Click Canvas
1. **Right-click** on the empty canvas area
2. Select **"New" → "Database" → "PostgreSQL"**

#### Option D: CMD + K (Mac) or CTRL + K (Windows)
1. Press **CMD + K** (Mac) or **CTRL + K** (Windows)
2. Type **"postgres"**
3. Select **"Add PostgreSQL"**

---

### Step 3: Wait for PostgreSQL to Provision

After clicking "Add PostgreSQL":

1. **A new box/card appears** labeled "Postgres" (or "PostgreSQL")
2. Railway shows a **progress indicator** (spinning icon or progress bar)
3. **Wait 30-60 seconds** for it to provision
4. When ready, the status changes to **"Active"** or shows a green indicator

**What you should see**:
```
┌─────────────────┐     ┌─────────────────┐
│   Your App      │     │    Postgres     │
│   (Python)      │     │   (Database)    │
│   Status: ?     │     │   Status: ●     │
└─────────────────┘     └─────────────────┘
```

---

### Step 4: Verify DATABASE_URL Was Added

Railway **automatically** injects the `DATABASE_URL` environment variable:

1. Click on your **main app service** (not the Postgres one)
2. Look for tabs at the top: **Settings, Variables, Deployments, Logs**, etc.
3. Click on the **"Variables"** tab
4. **Look for**: `DATABASE_URL`
5. You should see something like:
   ```
   DATABASE_URL = postgresql://postgres:PASSWORD@HOSTNAME:5432/railway
   ```

**If you DON'T see DATABASE_URL**:
- Make sure both services are in the **same project**
- Try refreshing the page
- Click "Generate Domain" on the Postgres service
- See troubleshooting section below

---

### Step 5: Trigger Redeployment

Your app needs to restart to use the new database:

1. Stay on your **main app service** page
2. Look for tabs: Settings, **Deployments**, Variables, etc.
3. Click **"Deployments"** tab
4. You should see a list of past deployments
5. Find the **latest deployment** (top of list)
6. Look for options like:
   - **"Redeploy"** button
   - **"Restart"** button
   - Three dots menu **"..."** → "Redeploy"
7. Click **"Redeploy"** or **"Restart"**

**Alternative**: Just push a new commit to GitHub (Railway auto-deploys)

---

### Step 6: Monitor Deployment Logs

Watch the logs to see if it works:

1. Click on your app service
2. Click the **"Logs"** tab (or "Deployments" → "View Logs")
3. Watch for these **GOOD** signs:
   ```
   ✓ Build succeeded
   ✓ Starting Container
   ✓ INFO: Using PostgreSQL connection pool (Railway production mode)
   ✓ INFO: Started server process
   ✓ INFO: Uvicorn running on http://0.0.0.0:XXXX
   ✓ Health check: Passed
   ```

4. Watch for these **BAD** signs:
   ```
   ✗ psycopg2.OperationalError: could not connect
   ✗ Invalid value for '--port': '$PORT'
   ✗ Health check: Failed
   ✗ Container crashed
   ```

---

### Step 7: Test the Backend

Once deployment shows **"Active"**:

```bash
# Test health endpoint
curl https://crisiskitai-production.up.railway.app/health

# Expected response:
{
  "status": "ok",
  "service": "crisiskit-api",
  "checks": {
    "database": {"status": "healthy"},
    "knowledge_base": {"status": "healthy", "chunks_count": 0}
  }
}
```

If you see `"database": {"status": "healthy"}` → **SUCCESS!** 🎉

---

## Method 2: Add PostgreSQL via Railway CLI

If the dashboard isn't working, use the command line:

### Install Railway CLI

**Mac/Linux**:
```bash
# Install via npm
npm install -g @railway/cli

# OR install via brew (Mac only)
brew install railway
```

**Windows**:
```powershell
# Install via npm (requires Node.js)
npm install -g @railway/cli
```

### Login and Link Project

```bash
# Login to Railway
railway login

# Navigate to your project directory
cd /home/rpas/projects/crisiskit_project

# Link to your Railway project
railway link
# Select your project from the list

# Verify you're linked
railway status
```

### Add PostgreSQL Database

```bash
# Add PostgreSQL plugin
railway add --database postgres

# This automatically:
# 1. Creates PostgreSQL instance
# 2. Injects DATABASE_URL variable
# 3. Links it to your project
```

### Trigger Redeployment

```bash
# Deploy current code
railway up

# OR: Trigger redeploy without changing code
railway redeploy
```

### Check Logs

```bash
# View logs in real-time
railway logs

# Look for "Using PostgreSQL connection pool"
```

---

## Method 3: Manual DATABASE_URL Setup (NOT RECOMMENDED)

If you have a PostgreSQL database elsewhere (not recommended):

1. Go to your app service → **Variables** tab
2. Click **"New Variable"**
3. Add:
   ```
   Variable: DATABASE_URL
   Value: postgresql://user:password@host:5432/dbname
   ```
4. Save
5. Redeploy

**This is NOT recommended** because:
- You have to manage the database yourself
- Railway's Postgres addon is free on Hobby plan
- Auto-backups and management are handled

---

## 🚨 Troubleshooting Common Issues

### Issue 1: "I don't see a 'New' button"

**Solution**:
- Try refreshing the page
- Make sure you're on the **project page** (not the dashboard home)
- Look for alternative methods (CMD+K, right-click, etc.)
- Try a different browser (Chrome/Firefox)
- Check if you're logged in to the right account

### Issue 2: "PostgreSQL provisioning failed"

**Solution**:
- Check your Railway plan (Hobby plan includes Postgres)
- Verify your account is in good standing
- Try deleting and re-adding the service
- Contact Railway support: https://railway.app/help

### Issue 3: "DATABASE_URL is not showing up"

**Solution**:
1. Make sure Postgres service is **Active** (not provisioning)
2. Both services must be in the **same project**
3. Click on Postgres service → **Connect** tab → Copy connection string
4. Manually add DATABASE_URL to your app's Variables tab

### Issue 4: "Backend still returns 502 after adding Postgres"

**Checklist**:
- [ ] Postgres service shows "Active" status
- [ ] DATABASE_URL variable exists in app service
- [ ] App was redeployed AFTER adding DATABASE_URL
- [ ] Logs show "Using PostgreSQL connection pool"
- [ ] No errors in deployment logs

If all checked but still 502:
- Check logs for specific error message
- See RAILWAY_TROUBLESHOOTING.md
- Try the SQLite fallback (see below)

### Issue 5: "Health check keeps failing"

**Common causes**:
1. **Port issue**: See railway.json fix (commit 6510c6d)
2. **Database connection**: Postgres not accessible
3. **Application crash**: Check logs for Python errors
4. **Timeout**: Health check taking too long

**Solution**:
```bash
# Get detailed logs
railway logs --follow

# Look for the ACTUAL error:
# - "could not connect to server" → Database issue
# - "Invalid value for '--port'" → Port issue (should be fixed)
# - Python traceback → Code error
```

---

## 🔄 SQLite Fallback (If Postgres Setup Fails)

If you can't get Postgres working, use SQLite temporarily:

### Option A: Remove DATABASE_URL Variable

1. Go to your app service → **Variables** tab
2. Find `DATABASE_URL`
3. Click the **X** or **Delete** button
4. Save
5. Redeploy

This makes the app fall back to SQLite mode.

**⚠️ WARNING**: SQLite on Railway **will lose data** on every restart!

### Option B: Revert Code Temporarily

```bash
# Revert to before PostgreSQL changes
git revert ec81864 6510c6d 36797a3
git push origin main
```

This removes all Postgres code and goes back to SQLite-only.

---

## ✅ Success Checklist

After adding PostgreSQL, verify:

- [ ] Postgres service shows "Active" in Railway dashboard
- [ ] DATABASE_URL appears in app Variables tab
- [ ] Latest deployment succeeded (no errors)
- [ ] Logs show "Using PostgreSQL connection pool"
- [ ] Logs show "INFO: Uvicorn running on..."
- [ ] Health check passes (no 502 error)
- [ ] `curl` to /health returns `{"status":"ok"}`
- [ ] Database check shows `"status":"healthy"`

**If ALL checked** → You're live! 🎉

**If ANY unchecked** → See RAILWAY_TROUBLESHOOTING.md

---

## 📞 Getting Help

If you're still stuck:

1. **Copy your Railway logs**:
   - Railway Dashboard → Your Service → Logs tab
   - Copy the last 50-100 lines

2. **Check environment variables**:
   - Variables tab → Screenshot or copy all variables

3. **Check this**:
   - What does Railway dashboard show for service status?
   - Do you see one or two services (app + postgres)?
   - What's the last error message in logs?

4. **Share this info** and we can debug further

---

## 🎯 Quick Reference

**Add Postgres (Dashboard)**:
```
Project → New → Database → Add PostgreSQL → Wait → Redeploy
```

**Add Postgres (CLI)**:
```bash
railway link
railway add --database postgres
railway up
```

**Test Backend**:
```bash
curl https://crisiskitai-production.up.railway.app/health
```

**Expected**: `{"status":"ok",...}`

---

**Next Steps**: Once Postgres is working, see DEPLOYMENT_QUICKFIX.md for Vercel frontend setup.
