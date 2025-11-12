# ✅ CrisisKit Production Deployment - User Checklist

**Last Updated**: 2025-10-27
**Status**: Awaiting your action to complete deployment

---

## 🎯 Your Mission

Get CrisisKit fully deployed and working in production.

**Current Status**:
- ✅ Code fixes: COMPLETE
- ⏳ Backend (Railway): Needs your help to add database
- ⏳ Frontend (Vercel): Needs domain and password settings

**Time Required**: 15-20 minutes total

---

## 📋 Part 1: Fix Backend (Railway) - CRITICAL

### Step 1: Add PostgreSQL Database

**Time**: 5-10 minutes
**Difficulty**: Easy (just clicking buttons)

1. Open your browser and go to: **https://railway.app/dashboard**

2. Find and click on your **CrisisKit project** (or whatever you named it)

3. You should see your services displayed as boxes/cards

4. **Add PostgreSQL**:
   - Look for a **"New"** button (usually top-right corner)
   - Click **"New"** → **"Database"** → **"Add PostgreSQL"**
   - Alternative: Press **Cmd+K** (Mac) or **Ctrl+K** (Windows), then type "postgres"

5. **Wait**: A new "Postgres" box appears. Wait 30-60 seconds for it to provision.
   - Status will change from "Provisioning" to "Active"
   - Green indicator means ready

6. **Check Variables**:
   - Click on your **main app service** (not the Postgres one)
   - Go to the **"Variables"** tab
   - Look for: `DATABASE_URL`
   - Should see something like: `postgresql://postgres:xxxxx@hostname:5432/railway`

7. **Redeploy**:
   - Stay on your app service
   - Go to **"Deployments"** tab
   - Find the latest deployment (top of list)
   - Click **"Redeploy"** button (or **"..."** menu → **"Redeploy"**)

8. **Watch Logs**:
   - Go to **"Logs"** tab
   - Look for these GOOD signs:
     - ✅ `Build succeeded`
     - ✅ `Using PostgreSQL connection pool`
     - ✅ `INFO: Uvicorn running on http://0.0.0.0:XXXX`
   - If you see these, SUCCESS!

**Need help?** See: `.agents/RAILWAY_POSTGRESQL_SETUP.md` for detailed step-by-step with screenshots descriptions.

---

### Step 2: Test Backend

**Time**: 1 minute

Once deployment shows "Active", test it:

```bash
curl https://crisiskitai-production.up.railway.app/health
```

**Expected Response**:
```json
{
  "status": "ok",
  "service": "crisiskit-api",
  "checks": {
    "database": {"status": "healthy"}
  }
}
```

**If you see this** → Backend is WORKING! ✅
**If you see 502** → Check logs, see troubleshooting guide

---

## 📋 Part 2: Fix Frontend (Vercel)

### Step 3: Configure Domain

**Time**: 3-5 minutes

1. Go to: **https://vercel.com/dashboard**

2. Find your **CrisisKit project** and click on it

3. Go to **Settings** → **Domains**

4. Check if `crisiskitai.vercel.app` is listed:
   - **If YES**: Make sure it's assigned to the Production environment
   - **If NO**: Add it:
     - Click **"Add"** or **"Add Domain"**
     - Enter: `crisiskitai.vercel.app`
     - Assign to **Production**
     - Save

5. Wait 2-3 minutes for DNS propagation

6. Test: Open browser and go to: **https://crisiskitai.vercel.app**
   - Should see your app (not 404)

---

### Step 4: Disable Password Protection

**Time**: 2 minutes

1. Stay in Vercel dashboard → Your CrisisKit project

2. Go to **Settings** → **Deployment Protection** (or **General**)

3. Look for **"Password Protection"** or **"Vercel Authentication"**

4. **Disable it**:
   - If there's a toggle, turn it OFF
   - If there's a password set, remove it
   - Save changes

5. Test: Try accessing your app without password
   - Should NOT see 401 Unauthorized
   - Should see the app directly

---

## 📋 Part 3: Final Verification

### Step 5: Full Integration Test

**Time**: 5 minutes

Test the complete flow:

1. **Test Backend Health**:
   ```bash
   curl https://crisiskitai-production.up.railway.app/health
   ```
   Expected: `{"status":"ok"}`

2. **Open Frontend**:
   - Go to: https://crisiskitai.vercel.app
   - Should load without errors

3. **Test Form Submission** (if applicable):
   - Fill out the intake form
   - Submit it
   - Verify plan generates successfully

4. **Check Backend Logs**:
   - Railway dashboard → Logs
   - Look for API requests being received
   - Should see no errors

---

## ✅ Success Checklist

Mark each item when complete:

### Backend (Railway)
- [ ] PostgreSQL service shows "Active" in Railway dashboard
- [ ] DATABASE_URL appears in app's Variables tab
- [ ] Latest deployment succeeded (no errors in logs)
- [ ] Logs show "Using PostgreSQL connection pool"
- [ ] Logs show "INFO: Uvicorn running on..."
- [ ] `/health` endpoint returns `{"status":"ok"}`
- [ ] Database check shows `"status":"healthy"`

### Frontend (Vercel)
- [ ] Domain crisiskitai.vercel.app is configured
- [ ] Password protection is disabled
- [ ] App loads at https://crisiskitai.vercel.app
- [ ] No 404 or 401 errors

### Integration
- [ ] Frontend can reach backend API
- [ ] Form submissions work end-to-end
- [ ] No errors in browser console
- [ ] No errors in Railway logs

**If ALL checked** → YOU'RE LIVE! 🎉🎉🎉

---

## 🚨 Troubleshooting

### Backend Still Shows 502

**Check these**:
1. Is Postgres service "Active"? (green indicator)
2. Is DATABASE_URL in your app's Variables tab?
3. Did you redeploy AFTER adding Postgres?
4. What do the logs say?

**See**: `.agents/RAILWAY_TROUBLESHOOTING.md` for detailed help

---

### Frontend Shows 404

**Check these**:
1. Is the domain `crisiskitai.vercel.app` in Settings → Domains?
2. Is it assigned to Production?
3. Try waiting 5 minutes for DNS propagation
4. Try clearing browser cache

---

### Frontend Shows 401

**Check these**:
1. Settings → Deployment Protection
2. Is password protection enabled?
3. Disable it and try again

---

### Still Stuck?

**Gather this info**:
1. Screenshot of Railway dashboard (your services)
2. Screenshot of Railway Variables tab
3. Last 50 lines of Railway logs
4. Screenshot of Vercel dashboard (domains)

**Then review**:
- `.agents/RAILWAY_POSTGRESQL_SETUP.md` - Detailed setup guide
- `.agents/RAILWAY_TROUBLESHOOTING.md` - Detailed troubleshooting
- `.agents/RAILWAY_CLI_COMMANDS.sh` - CLI alternative commands

---

## 🎯 Quick Commands

**Test backend health**:
```bash
curl https://crisiskitai-production.up.railway.app/health
```

**View Railway logs**:
```bash
railway logs --follow
```

**Railway status**:
```bash
railway status
```

**Redeploy**:
```bash
railway redeploy
```

---

## 📊 What Success Looks Like

**Railway Dashboard**:
```
┌─────────────────┐     ┌─────────────────┐
│   Your App      │     │    Postgres     │
│   (Backend)     │     │   (Database)    │
│   Status: ● ON  │     │   Status: ● ON  │
└─────────────────┘     └─────────────────┘
```

**Terminal**:
```bash
$ curl https://crisiskitai-production.up.railway.app/health
{
  "status": "ok",
  "service": "crisiskit-api",
  "checks": {
    "database": {"status": "healthy"},
    "knowledge_base": {"status": "healthy", "chunks_count": 0}
  }
}
```

**Browser**:
- Go to: https://crisiskitai.vercel.app
- App loads
- No password prompt
- No errors

**If you see all of this** → DEPLOYMENT COMPLETE! 🎉

---

## 📞 Need Help?

If you're stuck after following this guide:

1. Run diagnostics:
   ```bash
   source .agents/RAILWAY_CLI_COMMANDS.sh
   full_diagnostic
   ```

2. Check documentation:
   - Railway PostgreSQL Setup: `.agents/RAILWAY_POSTGRESQL_SETUP.md`
   - Troubleshooting Guide: `.agents/RAILWAY_TROUBLESHOOTING.md`
   - Technical Report: `.agents/reports/railway-debug-report.json`

3. Share:
   - Output of `railway logs`
   - Screenshots of Railway dashboard
   - Specific error messages

**Good luck! You got this!** 💪
