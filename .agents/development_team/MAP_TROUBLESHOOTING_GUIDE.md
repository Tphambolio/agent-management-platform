# CrisisKit Mapping Troubleshooting Guide

**Version:** 1.0
**Last Updated:** 2025-10-28
**Status:** Production Ready

---

## Table of Contents

1. [Quick Diagnosis](#quick-diagnosis)
2. [Common Errors](#common-errors)
3. [Environment Configuration](#environment-configuration)
4. [Token Setup Guide](#token-setup-guide)
5. [Production Deployment](#production-deployment)
6. [Testing Procedures](#testing-procedures)
7. [Advanced Troubleshooting](#advanced-troubleshooting)
8. [FAQ](#faq)

---

## Quick Diagnosis

### Symptom: Maps don't load (blank white/gray area)

**Check browser console (F12):**

```
Failed to load resource: 403
https://api.maptiler.com/maps/streets/style.json?key=
```

**Root Cause:** MapTiler API key is missing or invalid.

**Fix:** [Add MapTiler key to environment variables](#maptiler-api-key-setup)

---

### Symptom: Infrastructure suggestions fail

**Check browser console (F12):**

```
Access to fetch at 'https://crisiskitai-production.up.railway.app/infrastructure/suggest'
from origin 'https://crisiskitai.vercel.app'
has been blocked by CORS policy
```

**Root Cause:** Backend CORS configuration doesn't allow frontend domain.

**Fix:** [Update CORS configuration](#cors-configuration)

---

### Symptom: Address search doesn't work

**Check browser console (F12):**

```
MapBox geocoding API returned 401 Unauthorized
```

**Root Cause:** MapBox token is missing or invalid.

**Fix:** [Add MapBox token to environment variables](#mapbox-token-setup)

---

## Common Errors

### Error 1: MapTiler 403 Forbidden

```
GET https://api.maptiler.com/maps/streets/style.json?key= 403
```

**What it means:**
- MapTiler API key is missing (empty string after `?key=`)
- Or the key is invalid/expired

**How to fix:**

1. **Local development:**
   ```bash
   cd frontend
   # Edit .env.local
   echo "NEXT_PUBLIC_MAPTILER_KEY=your-key-here" >> .env.local
   npm run dev
   ```

2. **Vercel production:**
   - Go to https://vercel.com/dashboard
   - Select your CrisisKit project
   - Settings → Environment Variables
   - Add `NEXT_PUBLIC_MAPTILER_KEY` with your key
   - Select all environments (Production, Preview, Development)
   - Redeploy

**Where to get key:**
- Go to https://cloud.maptiler.com/account/keys/
- Create free account (10,000 requests/month free tier)
- Create new API key
- Add HTTP referrer restrictions (e.g., `*.vercel.app/*`, `localhost:*`)

---

### Error 2: CORS Policy Blocked

```
Access to fetch at 'https://crisiskitai-production.up.railway.app/infrastructure/suggest'
from origin 'https://crisiskitai.vercel.app' has been blocked by CORS policy
```

**What it means:**
- Backend doesn't allow requests from your frontend domain
- CORS configuration in `app.py` doesn't include your domain

**How to fix:**

1. Check `app.py` lines 177-188 for `ALLOWED_ORIGINS`:
   ```python
   ALLOWED_ORIGINS = [
       "http://localhost:3000",
       "http://127.0.0.1:3000",
       "https://crisiskitai.vercel.app",  # Add your domain here
       # ... other domains
   ]
   ```

2. Add your frontend domain to the list

3. Redeploy backend to Railway:
   ```bash
   git add app.py
   git commit -m "Add CORS origin for new domain"
   git push
   # Railway auto-deploys on push
   ```

4. Verify with curl:
   ```bash
   curl -H "Origin: https://your-frontend.vercel.app" \
        https://crisiskitai-production.up.railway.app/health \
        -v
   # Look for "Access-Control-Allow-Origin" in response headers
   ```

---

### Error 3: MapBox 401 Unauthorized

```
GET https://api.mapbox.com/geocoding/v5/mapbox.places/...?access_token=... 401
```

**What it means:**
- MapBox access token is missing or invalid
- Token doesn't have geocoding permissions

**How to fix:**

1. **Get/check token:**
   - Go to https://account.mapbox.com/access-tokens/
   - Create new token or use existing
   - Ensure "Geocoding" scope is enabled

2. **Add to environment:**
   ```bash
   # Local (.env.local)
   NEXT_PUBLIC_MAPBOX_TOKEN=pk.your-mapbox-token-here

   # Vercel (Environment Variables dashboard)
   NEXT_PUBLIC_MAPBOX_TOKEN = pk.your-mapbox-token-here
   ```

3. **Fallback behavior:**
   - If MapBox token is invalid/missing, app falls back to OpenStreetMap Nominatim
   - You'll see: "Mapbox token not detected; using OpenStreetMap lookup"
   - This is expected and works fine (just slower)

---

### Error 4: Map Tiles Not Loading (Network Errors)

```
GET https://api.maptiler.com/tiles/v3/.../tile.pbf net::ERR_FAILED
```

**What it means:**
- MapTiler API is down (rare)
- Network/firewall blocking MapTiler domain
- Rate limit exceeded (check MapTiler dashboard)

**How to fix:**

1. **Check MapTiler status:**
   - Go to https://status.maptiler.com/

2. **Check rate limits:**
   - Log into MapTiler account
   - Check usage dashboard
   - Free tier: 10,000 tile requests/month
   - Upgrade if exceeded

3. **Check API key restrictions:**
   - MapTiler account → API keys
   - Ensure HTTP referrer restrictions allow your domain
   - Example: `*.vercel.app/*`, `localhost:*`

---

### Error 5: GeoJSON Features Not Rendering

**Symptom:** Map loads but features don't appear

**Check browser console (F12):**
```
MapEditor: Map error: { type: 'error', error: {...} }
```

**Common causes:**

1. **Invalid GeoJSON structure:**
   ```json
   // BAD (missing geometry)
   {"type": "Feature", "properties": {"name": "Test"}}

   // GOOD
   {
     "type": "Feature",
     "geometry": {"type": "Point", "coordinates": [-114.07, 51.04]},
     "properties": {"name": "Test", "category": "Custom", "color": "#3b82f6"}
   }
   ```

2. **Invalid coordinates:**
   - Longitude must be -180 to 180
   - Latitude must be -90 to 90
   - Check for swapped lat/lng (common mistake)

3. **Feature outside map bounds:**
   - Map might be zoomed to wrong area
   - Use "Fit to features" or manual zoom

**How to fix:**

1. Validate GeoJSON:
   - Copy GeoJSON from localStorage or API response
   - Paste into https://geojson.io/
   - Check for errors

2. Check feature coordinates:
   ```javascript
   // In browser console
   const state = JSON.parse(localStorage.getItem('intakeState'));
   console.log(state.map.geojson.features);
   // Inspect coordinates
   ```

3. Force map recenter:
   ```javascript
   // In MapEditor.js, features should auto-fit
   // If not, manually set initialCenter prop
   ```

---

## Environment Configuration

### Development (.env.local)

```bash
# Backend API URL
NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000

# MapTiler API key (required for maps)
NEXT_PUBLIC_MAPTILER_KEY=your-maptiler-api-key-here

# MapBox token (optional, for geocoding)
NEXT_PUBLIC_MAPBOX_TOKEN=pk.your-mapbox-token-here

# Nominatim email (fallback geocoding)
NEXT_PUBLIC_NOMINATIM_EMAIL=your-email@example.com
```

**Setup:**
```bash
cd frontend
cp .env.example .env.local
# Edit .env.local with your keys
npm run dev
```

---

### Production (Vercel)

**DO NOT commit .env.local to git!**

Instead, set environment variables in Vercel dashboard:

1. Go to https://vercel.com/dashboard
2. Select your project
3. Settings → Environment Variables
4. Add each variable:

| Variable | Value | Environments |
|----------|-------|--------------|
| `NEXT_PUBLIC_API_BASE` | `https://crisiskitai-production.up.railway.app` | Production |
| `NEXT_PUBLIC_MAPTILER_KEY` | `your-maptiler-key` | All |
| `NEXT_PUBLIC_MAPBOX_TOKEN` | `pk.your-mapbox-token` | All |
| `NEXT_PUBLIC_NOMINATIM_EMAIL` | `your-email@example.com` | All |

5. Save and redeploy

**Note:** `NEXT_PUBLIC_` prefix makes variables available to client-side code (browser). This is intentional and safe for API keys that are meant to be public (with referrer restrictions).

---

### Backend (Railway)

Backend environment variables are set in Railway dashboard:

1. Go to https://railway.app/dashboard
2. Select your project
3. Variables tab
4. Add:

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection (auto-set) |
| `OPENAI_API_KEY` | `sk-...` | OpenAI API key (optional) |
| `GOOGLE_PLACES_API_KEY` | `AIza...` | Google Places API (optional) |

**Note:** Frontend environment variables are NOT set in Railway (they're in Vercel).

---

## Token Setup Guide

### MapTiler API Key Setup

**1. Create Account:**
- Go to https://cloud.maptiler.com/
- Sign up for free account
- Free tier: 10,000 tile requests/month (sufficient for development)

**2. Create API Key:**
- Go to https://cloud.maptiler.com/account/keys/
- Click "Create new key"
- Name: `CrisisKit Production` (or similar)
- Click "Create"

**3. Add HTTP Referrer Restrictions (Security):**
- Edit your API key
- Add referrer restrictions:
  ```
  https://crisiskitai.vercel.app/*
  https://*.vercel.app/*
  http://localhost:*
  http://127.0.0.1:*
  ```
- This prevents others from using your key

**4. Add to Environment:**
- **Vercel:** Settings → Environment Variables → Add `NEXT_PUBLIC_MAPTILER_KEY`
- **Local:** Add to `frontend/.env.local`

**5. Verify:**
```bash
# Check key is loaded (in browser console, after page load)
console.log(process.env.NEXT_PUBLIC_MAPTILER_KEY ? 'Key loaded' : 'Key missing');
```

---

### MapBox Token Setup

**1. Create Account:**
- Go to https://account.mapbox.com/
- Sign up for free account
- Free tier: 50,000 requests/month

**2. Create Access Token:**
- Go to https://account.mapbox.com/access-tokens/
- Click "Create a token"
- Name: `CrisisKit Geocoding`
- Scopes: Check "Geocoding" (styles:read is default)
- URL restrictions: Add your domains
  ```
  https://crisiskitai.vercel.app
  https://*.vercel.app
  http://localhost:3000
  ```
- Click "Create token"

**3. Add to Environment:**
- **Vercel:** Settings → Environment Variables → Add `NEXT_PUBLIC_MAPBOX_TOKEN`
- **Local:** Add to `frontend/.env.local`

**4. Verify:**
```bash
# In browser console
console.log(process.env.NEXT_PUBLIC_MAPBOX_TOKEN?.substring(0, 10)); // Should show "pk.eyJ1..."
```

**Note:** MapBox token is optional. If missing, app uses OpenStreetMap Nominatim fallback.

---

## Production Deployment

### Pre-Deployment Checklist

**Backend (Railway):**
- [ ] PostgreSQL database is provisioned
- [ ] Latest code is pushed to git (Railway auto-deploys)
- [ ] Health endpoint returns 200 OK: `curl https://crisiskitai-production.up.railway.app/health`
- [ ] CORS allows Vercel domains (check `app.py` lines 177-188)
- [ ] Environment variables are set (OPENAI_API_KEY, GOOGLE_PLACES_API_KEY if used)

**Frontend (Vercel):**
- [ ] Latest code is pushed to git (Vercel auto-deploys)
- [ ] Environment variables are set:
  - [ ] `NEXT_PUBLIC_API_BASE` → `https://crisiskitai-production.up.railway.app`
  - [ ] `NEXT_PUBLIC_MAPTILER_KEY` → Your MapTiler key
  - [ ] `NEXT_PUBLIC_MAPBOX_TOKEN` → Your MapBox token (optional)
  - [ ] `NEXT_PUBLIC_NOMINATIM_EMAIL` → Your email
- [ ] Build succeeds (check Vercel deployment logs)
- [ ] No environment variable warnings in build logs

---

### Deployment Steps

**1. Deploy Backend First:**

```bash
# Ensure latest code is committed
git add .
git commit -m "Deploy backend with CORS fixes"
git push

# Railway auto-deploys on push to main branch
# Monitor: https://railway.app/dashboard
```

**2. Verify Backend Health:**

```bash
# Check health endpoint
curl https://crisiskitai-production.up.railway.app/health
# Expected: {"status": "ok", ...}

# Check CORS
curl -H "Origin: https://crisiskitai.vercel.app" \
     https://crisiskitai-production.up.railway.app/health \
     -v | grep -i "access-control"
# Expected: Access-Control-Allow-Origin: https://crisiskitai.vercel.app
```

**3. Deploy Frontend:**

```bash
# Vercel auto-deploys on push to main branch
git push

# Or trigger manual deploy:
# Go to Vercel dashboard → Deployments → Redeploy
```

**4. Set Frontend Environment Variables:**

- Go to Vercel Dashboard → Your Project → Settings → Environment Variables
- Add all required variables (see [Environment Configuration](#environment-configuration))
- **Important:** Select "Production", "Preview", and "Development" for each variable
- Click "Save"
- Redeploy (Vercel will prompt)

**5. Verify Frontend:**

```bash
# Check frontend loads
curl -I https://crisiskitai.vercel.app
# Expected: 200 OK

# Check JavaScript bundle includes env vars (not recommended for production, but helpful for debugging)
curl https://crisiskitai.vercel.app/_next/static/chunks/main-*.js | grep "NEXT_PUBLIC_API_BASE"
# Should see your Railway URL
```

---

### Post-Deployment Verification

**Test Map Functionality:**

1. Open https://crisiskitai.vercel.app in browser
2. Open browser console (F12)
3. Navigate to intake form
4. Go to map editor step
5. **Check for errors:**
   - No 403 errors from MapTiler
   - No CORS errors from backend
   - Map tiles load correctly
6. **Test map interactions:**
   - Pan and zoom
   - Draw a point (click "Point" button, click map)
   - Draw a line (click "Line" button, click multiple points, double-click to finish)
   - Draw a polygon (click "Polygon" button, click multiple points, double-click to finish)
   - Select a feature (click it)
   - Delete a feature (select it, click trash button)
7. **Test infrastructure lookup:**
   - Click "Add Infrastructure" (if available)
   - Search for a facility
   - Verify results load (no CORS errors)
8. **Save and view results:**
   - Complete intake form
   - View result page
   - Verify map displays correctly with all features

**Test Geocoding:**

1. In intake form step 2 (incident context)
2. Enter an address in location field
3. Verify autocomplete suggestions appear
4. If MapBox token is set: Fast suggestions from MapBox
5. If MapBox token is missing: Slower suggestions from OSM Nominatim (with warning message)

---

## Testing Procedures

### Local Development Testing

```bash
# 1. Start backend
cd /home/rpas/projects/crisiskit_project
uvicorn app:app --reload

# 2. Start frontend (new terminal)
cd frontend
npm run dev

# 3. Open browser
open http://localhost:3000

# 4. Test map loading
# - Navigate to intake → map editor
# - Check browser console for errors
# - Verify map tiles load

# 5. Test API connectivity
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/mapping/1
```

---

### Production Testing

**Backend API Tests:**

```bash
# Health check
curl https://crisiskitai-production.up.railway.app/health

# Test CORS
curl -H "Origin: https://crisiskitai.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://crisiskitai-production.up.railway.app/mapping/1 \
     -v

# Test mapping endpoint (GET)
curl https://crisiskitai-production.up.railway.app/mapping/1?map_type=overview

# Test infrastructure endpoint (POST)
curl -X POST https://crisiskitai-production.up.railway.app/infrastructure/suggest \
     -H "Content-Type: application/json" \
     -H "Origin: https://crisiskitai.vercel.app" \
     -d '{"latitude": 51.0447, "longitude": -114.0719, "radius_km": 5, "categories": ["hospital"], "hazards": []}'
```

**Frontend Tests:**

1. **Map Tile Loading:**
   - Open https://crisiskitai.vercel.app
   - F12 → Network tab → Filter by "maptiler"
   - Navigate to map editor
   - Verify tile requests return 200 OK (not 403)

2. **GeoJSON Save/Load:**
   - Draw features on map
   - Complete intake form
   - View result page
   - Verify features appear on result map
   - Check localStorage: `localStorage.getItem('intakeState')`

3. **Infrastructure Lookup:**
   - In map editor, add infrastructure (if available)
   - Check Network tab for `/infrastructure/suggest` request
   - Verify 200 OK response
   - Verify no CORS errors

---

### Performance Testing

**Map Load Time:**

```javascript
// In browser console
performance.mark('map-start');
// ... wait for map to load ...
performance.mark('map-end');
performance.measure('map-load', 'map-start', 'map-end');
console.log(performance.getEntriesByName('map-load')[0].duration);
// Target: < 2000ms
```

**Tile Load Time:**

- F12 → Network tab → Filter by "pbf" (vector tiles)
- Check individual tile load times
- Target: < 500ms per tile

**API Response Time:**

```bash
# Test mapping endpoint
time curl https://crisiskitai-production.up.railway.app/mapping/1
# Target: < 500ms
```

---

## Advanced Troubleshooting

### Debug Mode

**Enable MapLibre GL Debug:**

```javascript
// In MapEditor.js or result page, add after map creation
map.showTileBoundaries = true;
map.showCollisionBoxes = true;
console.log('MapLibre GL version:', maplibregl.version);
```

**Enable Verbose Console Logging:**

```javascript
// In MapEditor.js, line 386+
console.log('MapEditor: Initializing map with style:', getInitialStyle());
console.log('MapEditor: MAPTILER_KEY present:', !!MAPTILER_KEY);
console.log('MapEditor: Initial center:', initialCenter);
```

---

### Clear Browser Cache

Sometimes old cached styles cause issues:

1. **Chrome:** F12 → Network tab → Check "Disable cache" → Refresh
2. **Firefox:** F12 → Network tab → Settings icon → Check "Disable HTTP cache" → Refresh
3. **Full clear:** Settings → Privacy → Clear browsing data → Cached images and files

---

### Inspect GeoJSON Data

**From localStorage:**

```javascript
// In browser console
const state = JSON.parse(localStorage.getItem('intakeState'));
console.log('GeoJSON:', state.map.geojson);
console.log('Features:', state.map.geojson.features);
console.log('Legend:', state.map.legend);
```

**From API:**

```bash
# Get GeoJSON for submission ID 1
curl https://crisiskitai-production.up.railway.app/mapping/1?map_type=overview | jq .geojson
```

**Validate GeoJSON:**

```bash
# Copy GeoJSON output
# Paste into https://geojson.io/
# Visual validation + schema check
```

---

### Check Map Styles

**Inspect loaded style:**

```javascript
// In browser console (after map loads)
const map = mapRef.current; // or window.map if exposed
console.log('Map style:', map.getStyle());
console.log('Map sources:', Object.keys(map.getStyle().sources));
console.log('Map layers:', map.getStyle().layers.map(l => l.id));
```

**Verify MapTiler style loads:**

```bash
# Check style JSON (replace key)
curl "https://api.maptiler.com/maps/streets/style.json?key=YOUR_KEY" | jq .sources
# Should return sources like "openmaptiles"
```

---

### Network Analysis

**Check all API calls:**

1. F12 → Network tab
2. Filter by "Fetch/XHR"
3. Navigate through app
4. Look for failed requests (red)
5. Click request → Preview tab to see response
6. Check response headers for CORS headers

**Common API calls to monitor:**

- `/health` - Backend health check
- `/mapping/{id}` - Get GeoJSON
- `/mapping/{id}` (POST) - Save GeoJSON
- `/infrastructure/suggest` - POI lookup
- `/weather` - Weather forecast
- `api.maptiler.com/maps/.../style.json` - Map style
- `api.maptiler.com/tiles/...` - Map tiles
- `api.mapbox.com/geocoding/...` - Geocoding

---

### Backend Logs

**Railway logs:**

1. Go to https://railway.app/dashboard
2. Select your project
3. Click "Logs" tab
4. Filter by error/warning
5. Look for:
   - CORS errors
   - Database errors
   - API key errors
   - Rate limit warnings

**Local backend logs:**

```bash
# Run backend with verbose logging
uvicorn app:app --reload --log-level debug
```

---

## FAQ

### Q: Map loads but tiles are blurry/pixelated

**A:** This is normal at low zoom levels. Zoom in for higher resolution tiles. If still blurry:
- Check device pixel ratio (retina displays use @2x tiles)
- Verify MapTiler plan includes high-DPI tiles

---

### Q: Can I use MapBox GL instead of MapLibre GL?

**A:** MapLibre GL is an open-source fork of MapBox GL v1. Current implementation uses MapLibre GL v3.6.2. MapBox GL v3+ requires a paid license. Stick with MapLibre GL for free, OSS-friendly solution.

---

### Q: How many map tiles can I load per month?

**A:**
- **MapTiler Free:** 10,000 tile requests/month
- **MapTiler Basic:** 100,000 tile requests/month ($29)
- Each map view loads ~20-50 tiles depending on zoom level
- Free tier = ~200-500 map views/month

---

### Q: Do I need both MapTiler and MapBox tokens?

**A:**
- **MapTiler:** Required for map display (base layer tiles)
- **MapBox:** Optional for geocoding (address search)
- If you omit MapBox, app falls back to OpenStreetMap Nominatim (free, slower)

---

### Q: Can I self-host map tiles?

**A:** Yes, but complex:
1. Download OpenStreetMap data for your region
2. Set up tile server (e.g., Tileserver GL, Martin)
3. Update MapLibre style JSON to point to your server
4. Significant storage/bandwidth requirements

**Recommendation:** Use MapTiler free tier for development/testing, upgrade if needed.

---

### Q: How do I add a custom basemap style?

**A:**

1. Create custom style at https://cloud.maptiler.com/maps/ or https://mapbox.com/studio/
2. Get style JSON URL
3. Update `MapEditor.js`:
   ```javascript
   const BASEMAP_STYLES = {
     streets: `https://api.maptiler.com/maps/streets/style.json?key=${MAPTILER_KEY}`,
     satellite: `https://api.maptiler.com/maps/hybrid/style.json?key=${MAPTILER_KEY}`,
     custom: `https://api.maptiler.com/maps/YOUR_CUSTOM_MAP/style.json?key=${MAPTILER_KEY}`,
   };
   ```
4. Add dropdown option in UI

---

### Q: Map works locally but not in production

**A:** Check:
1. Environment variables set in Vercel (not just .env.local)
2. CORS allows production domain in backend
3. API keys have correct referrer restrictions
4. Backend is deployed and healthy
5. Browser console for specific errors

---

### Q: How do I migrate from SQLite to PostgreSQL?

**A:** Already done! Backend now uses PostgreSQL in production:
- Railway automatically provisions PostgreSQL
- `DATABASE_URL` environment variable set by Railway
- Schema migrations handled by `init_db()` on startup

---

### Q: GeoJSON features disappear after refresh

**A:** This is expected behavior:
- Features are stored in localStorage (frontend)
- Not persisted to backend until form submission
- After submission, features are saved to database
- Result page loads features from database

To persist earlier:
- Call `POST /mapping/{submission_id}` to save GeoJSON
- Requires submission_id (created on initial form submit)

---

### Q: Can I import existing GeoJSON files?

**A:** Not currently implemented in UI. Workaround:
1. Open browser console
2. Load GeoJSON:
   ```javascript
   const myGeoJSON = { type: "FeatureCollection", features: [...] };
   const state = JSON.parse(localStorage.getItem('intakeState'));
   state.map.geojson = myGeoJSON;
   localStorage.setItem('intakeState', JSON.stringify(state));
   location.reload();
   ```

Feature request: Add "Import GeoJSON" button in MapEditor UI.

---

### Q: How do I export GeoJSON?

**A:** Two ways:

1. **From browser:**
   ```javascript
   const state = JSON.parse(localStorage.getItem('intakeState'));
   console.log(JSON.stringify(state.map.geojson, null, 2));
   // Copy output
   ```

2. **From API:**
   ```bash
   curl https://crisiskitai-production.up.railway.app/mapping/1?map_type=overview | jq .geojson > map.geojson
   ```

---

### Q: Rate limiting on infrastructure endpoint

**Error:** `429 Too Many Requests`

**A:** Infrastructure endpoint is rate-limited to 10 requests/minute (per IP):
- Wait 1 minute and retry
- If legitimate high usage, increase limit in `app.py` line 1676:
  ```python
  @limiter.limit("10/minute")  # Change to "20/minute" or higher
  ```

---

### Q: 3D buildings don't show

**A:** 3D buildings require:
1. Zoom level >= 15 (zoom in close)
2. MapTiler style includes building data (streets style does)
3. "3D Buildings" checkbox enabled in UI
4. Building source available in style

Check console for:
```
MapEditor: 3D buildings not available: ...
```

If error, the basemap style doesn't support 3D buildings.

---

## Getting Help

**Still stuck? Check these resources:**

1. **Project documentation:** `CLAUDE.md` in repo root
2. **MapLibre GL docs:** https://maplibre.org/maplibre-gl-js/docs/
3. **MapTiler docs:** https://docs.maptiler.com/
4. **GeoJSON spec:** https://geojson.org/
5. **Railway support:** https://help.railway.app/
6. **Vercel support:** https://vercel.com/support

**Report bugs:**
- Create GitHub issue with:
  - Browser console errors
  - Network tab screenshots
  - Steps to reproduce
  - Environment (dev vs production)

---

## Changelog

**v1.0 (2025-10-28):**
- Initial comprehensive troubleshooting guide
- Covers MapTiler 403 errors (production issue)
- CORS configuration guide
- Token setup procedures
- Production deployment checklist
- Advanced debugging techniques

---

**Document maintained by:** Mapping Agent
**Last reviewed:** 2025-10-28
**Next review:** After production verification
