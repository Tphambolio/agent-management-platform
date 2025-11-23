# Google OAuth Setup Guide

## Overview
This guide walks you through setting up Google OAuth authentication for the Agent Management Platform, allowing users to sign in with their Google account and use their own Gemini API quota.

## Step 1: Google Cloud Console Setup

### 1.1 Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a project" → "New Project"
3. Enter project name: `agent-management-platform`
4. Click "Create"

### 1.2 Enable Required APIs

1. In your project, go to **APIs & Services** → **Library**
2. Search for and enable:
   - **Google+ API** (for user profile)
   - **Generative Language API** (for Gemini)

### 1.3 Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. If prompted, configure OAuth consent screen first:
   - User Type: **External**
   - App name: `Agent Management Platform`
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add these scopes:
     - `openid`
     - `email`
     - `profile`
     - `https://www.googleapis.com/auth/generative-language.retriever`
   - Test users: Add your email (for testing)

4. Back to Create OAuth client ID:
   - Application type: **Web application**
   - Name: `Agent Platform Web Client`
   - Authorized redirect URIs:
     - Local: `http://localhost:8000/api/auth/google/callback`
     - Production: `https://your-backend.onrender.com/api/auth/google/callback`

5. Click **Create**
6. **Copy your Client ID and Client Secret** - you'll need these!

## Step 2: Configure Environment Variables

### 2.1 For Render Deployment

Go to your Render dashboard → Backend service → Environment → Add these:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=https://your-backend.onrender.com/api/auth/google/callback
FRONTEND_URL=https://your-frontend.onrender.com

# Encryption (generate a strong secret)
SECRET_KEY=your-very-long-random-secret-at-least-32-characters
```

### 2.2 For Local Development

Add to `backend/.env`:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
FRONTEND_URL=http://localhost:5173

# Encryption
SECRET_KEY=local-dev-secret-key-change-in-production
```

## Step 3: Update Database Schema

Run the migration script to add OAuth fields to the users table:

```bash
cd /home/rpas/agent-management-platform
python backend/add_oauth_fields.py
```

This adds:
- `google_id` (unique identifier from Google)
- `google_access_token_encrypted` (for Gemini API calls)
- `google_refresh_token_encrypted` (to refresh expired tokens)
- `token_expires_at` (token expiration timestamp)
- `profile_picture` (user's Google profile picture)

## Step 4: Update CORS Settings

Make sure your backend's CORS settings allow your frontend domain with credentials:

In `backend/app/main.py`, ensure:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-frontend.onrender.com"
    ],
    allow_credentials=True,  # Important for cookies!
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Step 5: Test the OAuth Flow

### Local Testing

1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Open `http://localhost:5173`
4. Click "Sign in with Google"
5. Authorize the app
6. You should be redirected back and see your profile

### Production Testing

1. Deploy to Render (push to main branch)
2. Open your production frontend URL
3. Click "Sign in with Google"
4. Authorize the app
5. Verify authentication works

## Step 6: Verify Token Storage

After signing in, check that tokens are stored:

```sql
SELECT
  id,
  email,
  google_id,
  token_expires_at,
  google_access_token_encrypted IS NOT NULL as has_access_token,
  google_refresh_token_encrypted IS NOT NULL as has_refresh_token
FROM users
WHERE google_id IS NOT NULL;
```

## How It Works

### Authentication Flow

```
1. User clicks "Sign in with Google"
   → Frontend redirects to backend /api/auth/google

2. Backend redirects to Google OAuth consent screen
   → User authorizes app access

3. Google redirects back to backend with authorization code
   → Backend at /api/auth/google/callback

4. Backend exchanges code for access + refresh tokens
   → Stores encrypted tokens in database
   → Creates session cookie
   → Redirects to frontend with success

5. Frontend checks authentication
   → Calls /api/auth/session with cookie
   → Displays user profile
```

### Token Management

- **Access Token**: Used for Gemini API calls, expires in ~1 hour
- **Refresh Token**: Used to get new access tokens, lasts much longer
- **Automatic Refresh**: Backend checks expiration and refreshes automatically
- **Session Cookie**: HTTPOnly cookie for 7 days

## API Endpoints

### Frontend Usage

```javascript
// Check if user is authenticated
const response = await fetch(`${API_URL}/api/auth/session`, {
  credentials: 'include'  // Send cookies
});
const user = await response.json();

// Logout
await fetch(`${API_URL}/api/auth/logout`, {
  method: 'POST',
  credentials: 'include'
});
```

### Backend Usage (Internal)

```python
# Get user's Google token (auto-refreshes if expired)
from fastapi import Cookie
from app.routes.auth import get_user_token

token_data = await get_user_token(session_id=cookie_value, db=db)
access_token = token_data["access_token"]

# Use token with Gemini API
import google.generativeai as genai
genai.configure(api_key=access_token)
model = genai.GenerativeModel('gemini-2.5-flash')
```

## Security Features

✅ **Encrypted Storage**: All tokens encrypted with Fernet (AES-128)
✅ **HTTPOnly Cookies**: Session cookies not accessible to JavaScript
✅ **HTTPS Only**: Cookies only sent over HTTPS in production
✅ **Token Refresh**: Automatic refresh before expiration
✅ **Secure Secrets**: SECRET_KEY for encryption key derivation

## Troubleshooting

### "OAuth not configured" error
→ Check that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set

### "Failed to exchange code for token"
→ Verify redirect URI matches exactly in Google Cloud Console

### "Not authenticated" errors
→ Ensure CORS `allow_credentials=True` and frontend sends `credentials: 'include'`

### Tokens not persisting
→ Check that database migration was run successfully

### "No refresh token" error
→ OAuth consent must use `access_type=offline` and `prompt=consent`

## Next Steps

1. ✅ Set up Google Cloud project and OAuth credentials
2. ✅ Add environment variables to Render
3. ✅ Run database migration
4. ✅ Test authentication flow
5. ✅ Update any API calls to use user tokens
6. 🔄 Remove system-wide GEMINI_API_KEY (optional - keep as fallback)
7. 🔄 Add rate limiting per user
8. 🔄 Monitor token usage and quota

## User Benefits

🎯 **Personal Quota**: Each user uses their own free Gemini API quota
🎯 **No Shared Limits**: No more fighting over system-wide rate limits
🎯 **Privacy**: User data stays with their Google account
🎯 **Easy Onboarding**: One-click Google sign-in, no manual key entry

---

**Questions?** Check the implementation files:
- Backend OAuth: `backend/app/routes/auth.py`
- Frontend Component: `frontend/src/components/GoogleAuth.jsx`
- User Model: `backend/app/models.py`
- Token Management: `backend/app/user_credentials.py`
