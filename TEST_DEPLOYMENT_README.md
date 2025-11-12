# Deployment Testing Guide

## Overview

The `test-deployment.js` script automatically tests your entire Agent Management Platform deployment to identify issues.

## What It Tests

### Backend (Railway)
- ✓ Health endpoint (`/health`)
- ✓ Root endpoint (`/`)
- ✓ API endpoints (`/api/agents`)
- ✓ CORS configuration
- ✓ API documentation (`/docs`)

### Frontend (Vercel)
- ✓ Page loading
- ✓ React app structure
- ✓ JavaScript assets
- ✓ Static assets configuration

### Integration
- ✓ Frontend-backend communication
- ✓ CORS headers
- ✓ API accessibility

## How to Run

### From Your Local Machine

```bash
cd ~/wildfire-simulator-v2/agent-management-platform
node test-deployment.js
```

### With Custom URLs

```bash
BACKEND_URL=https://your-backend.railway.app \
FRONTEND_URL=https://your-frontend.vercel.app \
node test-deployment.js
```

## Understanding the Output

### Status Indicators

- `✓` **PASS** (Green) - Test passed successfully
- `✗` **FAIL** (Red) - Test failed, needs attention
- `⚠` **WARN** (Yellow) - Potential issue, but not critical

### Sample Output

```
✓ Backend Health Endpoint
  Status: healthy, Agents: 3

✗ Backend CORS Configuration
  No Access-Control-Allow-Origin header found

✓ Frontend Loading
  HTML page returned successfully
```

## Common Issues and Fixes

### Backend Not Accessible (502/503)

**Symptoms:**
- `✗ Backend Health Endpoint - 502 Bad Gateway`
- `✗ Backend Root Endpoint - 503 Service Unavailable`

**Solutions:**
1. Check Railway deployment logs for errors
2. Verify Dockerfile builds successfully
3. Check if container crashes on startup
4. Look for Python import errors or missing dependencies

### CORS Errors

**Symptoms:**
- `✗ Backend CORS Configuration - No Access-Control-Allow-Origin header`
- Browser console shows CORS errors

**Solutions:**
1. Add `CORS_ORIGINS` environment variable in Railway
2. Set value to your frontend URL (e.g., `https://your-app.vercel.app`)
3. Redeploy backend

### Frontend 404 Errors

**Symptoms:**
- `✗ Frontend Loading - 404 Not Found`
- Page shows blank or 404

**Solutions:**
1. Check Vercel deployment logs
2. Verify `npm run build` completed successfully
3. Check that `dist/` folder was created
4. Verify Vercel configuration (vercel.json)

### Frontend-Backend Communication Fails

**Symptoms:**
- `✗ Frontend-Backend Communication - Backend returned status: XXX`
- Frontend can't fetch data from backend

**Solutions:**
1. Verify `VITE_API_URL` environment variable in Vercel
2. Check CORS is properly configured on backend
3. Ensure backend URL is correct and accessible
4. Check browser network tab for actual errors

## Automated Recommendations

The test script provides specific recommendations based on failures:

```
RECOMMENDED ACTIONS:

Backend Issues Detected:
1. Check Railway deployment logs for errors
2. Verify CORS_ORIGINS environment variable is set
3. Ensure Dockerfile builds successfully
4. Check if container is crashing on startup
```

## Exit Codes

- **0** - All tests passed
- **1** - One or more tests failed

Use in CI/CD:
```bash
node test-deployment.js && echo "Deploy successful!" || echo "Deploy failed!"
```

## Continuous Monitoring

Run this test:
- After every deployment
- When changing environment variables
- When debugging production issues
- As part of your CI/CD pipeline

## Troubleshooting the Test Script

### DNS Resolution Errors

If you see `getaddrinfo EAI_AGAIN` errors:
- You're likely running from a container without network access
- Run from your local machine instead
- Ensure you have internet connectivity

### Timeout Errors

If tests time out:
- Check if the services are actually running
- Increase timeout in the script (currently 10 seconds)
- Check your internet connection

### SSL/Certificate Errors

If you see SSL errors:
- Verify the URLs use `https://`
- Check if certificates are valid
- Try accessing URLs in a browser first

## Need Help?

If the test script identifies issues but you're unsure how to fix them:
1. Check the Railway/Vercel dashboards for detailed logs
2. Review the deployment documentation
3. Check the browser console for client-side errors
4. Review network tab in browser developer tools
