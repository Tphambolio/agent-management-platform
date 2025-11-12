# CrisisKit Mapping - User Action Checklist

**Status:** REQUIRES USER ACTION
**Priority:** P0 - CRITICAL (Maps broken in production)
**Estimated Time:** 15-20 minutes

---

## Critical Issue Summary

Your maps are not loading in production because the **MapTiler API key is not set in Vercel environment variables**. This was caused by a recent security fix that removed a hardcoded API key from the code (commit 1244ff6).

**What you'll see:**
- Blank/gray map area in production
- Browser console error: `403 Forbidden` from `api.maptiler.com`
- Map works locally (if you have .env.local configured)

---

## Required Actions

### Action 1: Get MapTiler API Key (5 minutes)

**Priority:** P0 - CRITICAL

1. Go to https://cloud.maptiler.com/
2. Create free account (or log in if you have one)
   - Free tier: 10,000 tile requests/month (sufficient for development)
3. Go to https://cloud.maptiler.com/account/keys/
4. Click "Create new key"
5. Name it: `CrisisKit Production`
6. Click "Create"
7. **Copy the key** (starts with a random string)
8. Click "Edit" on your new key
9. Add HTTP referrer restrictions (security):
   ```
   https://crisiskitai.vercel.app/*
   https://*.vercel.app/*
   http://localhost:*
   http://127.0.0.1:*
   ```
10. Save restrictions

**Keep this key handy for the next step!**

---

### Action 2: Add MapTiler Key to Vercel (5 minutes)

**Priority:** P0 - CRITICAL

1. Go to https://vercel.com/dashboard
2. Select your **CrisisKit** project
3. Click **Settings** (left sidebar)
4. Click **Environment Variables** (left sidebar)
5. Click **Add New**
6. Fill in:
   - **Key:** `NEXT_PUBLIC_MAPTILER_KEY`
   - **Value:** [Paste your MapTiler key from Action 1]
   - **Environment:** Check all three boxes:
     - ✅ Production
     - ✅ Preview
     - ✅ Development
7. Click **Save**
8. Vercel will prompt: "Redeploy to apply changes?"
9. Click **Redeploy** (or manually trigger redeploy from Deployments tab)

**Wait for redeployment to complete (1-2 minutes)**

---

### Action 3: Verify Maps Work (5 minutes)

**Priority:** P0 - CRITICAL

1. Open https://crisiskitai.vercel.app (your production URL)
2. Open browser console (F12)
3. Navigate to: **Start New Plan** → **Step 6: Map**
4. **Check console for errors:**
   - ❌ **Before fix:** `403 Forbidden` from `api.maptiler.com`
   - ✅ **After fix:** No 403 errors, map tiles load
5. **Test map interactions:**
   - Pan and zoom map
   - Click "Point" button, click map to add a point
   - Click "Line" button, click multiple points, double-click to finish
   - Click "Polygon" button, click multiple points, double-click to finish
6. **Test basemap switcher:**
   - Change from "Streets" to "Satellite"
   - Verify tiles load correctly
7. **Complete form and view result page:**
   - Fill out remaining form fields
   - Click "Generate Plan"
   - Go to "Maps" tab on result page
   - Verify map displays with all features

**If all tests pass, Action 3 is complete!**

---

### Action 4: Verify Railway Backend (Optional, 3 minutes)

**Priority:** P1 - HIGH (not blocking maps, but needed for infrastructure lookup)

**Background:** You mentioned Railway was returning 503 earlier. Recent PostgreSQL migration should have fixed this. Let's verify.

1. Open terminal
2. Run health check:
   ```bash
   curl https://crisiskitai-production.up.railway.app/health
   ```
3. **Expected response:**
   ```json
   {
     "status": "ok",
     "database": "connected",
     "timestamp": "2025-10-28T..."
   }
   ```
4. If you get 503 or connection error:
   - Go to https://railway.app/dashboard
   - Check deployment status
   - Check logs for errors
   - May need to manually redeploy

5. Test CORS (to verify Vercel can access backend):
   ```bash
   curl -H "Origin: https://crisiskitai.vercel.app" \
        https://crisiskitai-production.up.railway.app/health \
        -v | grep -i "access-control"
   ```
6. **Expected:** `Access-Control-Allow-Origin: https://crisiskitai.vercel.app`

**If health check passes and CORS header is present, Action 4 is complete!**

---

## Optional Actions (Nice to Have)

### Optional 1: Add MapTiler Key to Local Development (2 minutes)

**Priority:** P2 - MEDIUM

If you work on the project locally and want maps to work in development:

1. Open `frontend/.env.local` in your text editor
2. Add this line:
   ```
   NEXT_PUBLIC_MAPTILER_KEY=your-maptiler-key-here
   ```
3. Save file
4. Restart dev server:
   ```bash
   cd frontend
   npm run dev
   ```
5. Test: http://localhost:3000

---

### Optional 2: Verify MapBox Token (2 minutes)

**Priority:** P2 - MEDIUM

MapBox token is used for address search (geocoding). It's optional - if missing, the app falls back to OpenStreetMap.

**Check if it's set in Vercel:**

1. Go to Vercel Dashboard → CrisisKit → Settings → Environment Variables
2. Look for `NEXT_PUBLIC_MAPBOX_TOKEN`
3. If present: ✅ You're good!
4. If missing: Follow steps below

**To add MapBox token:**

1. Go to https://account.mapbox.com/access-tokens/
2. Create account (or log in)
3. Create new token:
   - Name: `CrisisKit Geocoding`
   - Scopes: ✅ Geocoding
4. Add URL restrictions:
   ```
   https://crisiskitai.vercel.app
   https://*.vercel.app
   http://localhost:3000
   ```
5. Copy token (starts with `pk.`)
6. Add to Vercel:
   - Key: `NEXT_PUBLIC_MAPBOX_TOKEN`
   - Value: [Your MapBox token]
   - Environments: All three
7. Save and redeploy

---

### Optional 3: Add Production Environment File (2 minutes)

**Priority:** P2 - MEDIUM

Your `.env.production` file is missing `NEXT_PUBLIC_MAPTILER_KEY`. While Vercel doesn't read this file (it uses dashboard variables), it's good practice to keep it updated for documentation.

1. Open `frontend/.env.production` in text editor
2. Add this line:
   ```
   NEXT_PUBLIC_MAPTILER_KEY=your-maptiler-key-here
   ```
3. Save file
4. Commit to git:
   ```bash
   cd frontend
   git add .env.production
   git commit -m "Add NEXT_PUBLIC_MAPTILER_KEY to production env template"
   git push
   ```

**Note:** `.env.production` is just a template/documentation. Actual production values come from Vercel dashboard.

---

## Verification Checklist

Mark each item as you complete it:

### Critical (Must Complete)

- [ ] **MapTiler API key obtained** from https://cloud.maptiler.com/account/keys/
- [ ] **HTTP referrer restrictions added** to MapTiler key
- [ ] **NEXT_PUBLIC_MAPTILER_KEY added to Vercel** (all environments)
- [ ] **Vercel redeployed** after adding environment variable
- [ ] **Production map loads without 403 errors** in browser console
- [ ] **Map interactions work** (pan, zoom, draw features)
- [ ] **Result page map displays correctly** with saved features

### Optional (Nice to Have)

- [ ] **Railway backend health check passes** (no 503 errors)
- [ ] **CORS allows Vercel domain** (check curl command above)
- [ ] **Local development .env.local updated** with MapTiler key
- [ ] **MapBox token verified/added** (for geocoding)
- [ ] **.env.production updated** (documentation)

---

## Troubleshooting

### Issue: "Map still doesn't load after adding key"

**Try these:**

1. **Clear browser cache:**
   - Chrome: F12 → Network tab → Check "Disable cache" → Refresh
   - Or: Settings → Privacy → Clear cached images and files

2. **Verify key was saved in Vercel:**
   - Go to Vercel → Settings → Environment Variables
   - Check `NEXT_PUBLIC_MAPTILER_KEY` exists
   - Verify value is correct (no extra spaces)

3. **Verify redeployment completed:**
   - Go to Vercel → Deployments
   - Check latest deployment status
   - Should say "Ready" with green checkmark

4. **Check browser console:**
   - F12 → Console tab
   - Look for specific error messages
   - Share error message if still stuck

---

### Issue: "Railway backend returns 503"

**Try these:**

1. **Check Railway dashboard:**
   - Go to https://railway.app/dashboard
   - Check deployment status
   - Look for "Crashed" or "Failed" status

2. **Check Railway logs:**
   - Click "Logs" tab
   - Look for recent errors
   - Common issues:
     - Database connection failed
     - Environment variable missing
     - Import error

3. **Manually redeploy:**
   - Railway dashboard → Three dots menu → "Redeploy"
   - Wait for deployment to complete

4. **Check database connection:**
   - Railway dashboard → Variables tab
   - Verify `DATABASE_URL` is set (auto-set by Railway)

---

### Issue: "Maps work but infrastructure lookup fails"

**This is expected if Railway backend has issues:**

1. Complete **Action 4** above (verify Railway backend)
2. Check browser console for CORS errors
3. If CORS error appears:
   - Backend needs latest code deployed (CORS fix is in commit)
   - Go to Railway dashboard → Redeploy

---

## Need More Help?

**Resources:**

1. **Detailed troubleshooting:** See `.agents/MAP_TROUBLESHOOTING_GUIDE.md`
2. **Full diagnostic report:** See `.agents/reports/mapping-agent-diagnostic-report.json`
3. **MapTiler docs:** https://docs.maptiler.com/
4. **Vercel docs:** https://vercel.com/docs/environment-variables

**Contact:**

If you're still stuck after following this checklist:
1. Check browser console for specific error messages
2. Share error messages + screenshots
3. Note which actions you completed
4. Note which actions failed

---

## Summary

**What was broken:**
- MapTiler API key removed from code for security (commit 1244ff6)
- Key not set in Vercel environment variables
- Production maps returned 403 Forbidden

**What you need to do:**
1. ✅ Get MapTiler API key (5 min)
2. ✅ Add key to Vercel environment variables (5 min)
3. ✅ Redeploy Vercel (automatic)
4. ✅ Verify maps work in production (5 min)

**Estimated total time:** 15-20 minutes

**After completing these actions, your production maps should work perfectly!**

---

**Checklist created by:** Mapping Agent
**Date:** 2025-10-28
**Last updated:** 2025-10-28
