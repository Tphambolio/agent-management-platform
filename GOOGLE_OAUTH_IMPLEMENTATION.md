# Google OAuth Implementation Plan

## Overview
Implementing Google OAuth to allow users to authenticate and use their Google account to access Gemini API.

## Architecture

### 1. Google OAuth Flow
```
User clicks "Sign in with Google"
  ↓
Redirect to Google OAuth consent screen
  ↓
User approves access
  ↓
Google redirects back with authorization code
  ↓
Backend exchanges code for access token + refresh token
  ↓
Store tokens in database (encrypted)
  ↓
Use token to call Gemini API on user's behalf
```

### 2. Required Scopes
- `openid` - Basic OAuth
- `email` - User email
- `profile` - User profile info
- `https://www.googleapis.com/auth/generative-language.retriever` - Gemini API access

### 3. Setup Requirements

**Google Cloud Console:**
1. Create project at https://console.cloud.google.com
2. Enable Google+ API and Generative Language API
3. Create OAuth 2.0 credentials
4. Add authorized redirect URI: `https://your-backend.onrender.com/auth/google/callback`
5. Get Client ID and Client Secret

**Environment Variables:**
```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=https://your-backend.onrender.com/auth/google/callback
SESSION_SECRET=your-session-secret-key
```

## Implementation Files

### Backend Files to Create/Modify:
1. `backend/app/routes/auth.py` - OAuth endpoints
2. `backend/app/models.py` - Add User model
3. `backend/app/middleware/auth.py` - Session middleware
4. `backend/app/main.py` - Register auth routes

### Frontend Files to Create/Modify:
1. `frontend/src/components/GoogleAuth.tsx` - Login button
2. `frontend/src/hooks/useAuth.ts` - Auth state management
3. `frontend/src/App.tsx` - Protected routes

## Database Schema

**users table:**
```sql
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    google_id VARCHAR UNIQUE NOT NULL,
    email VARCHAR NOT NULL,
    name VARCHAR,
    profile_picture VARCHAR,
    google_access_token_encrypted TEXT,
    google_refresh_token_encrypted TEXT,
    token_expires_at TIMESTAMP,
    created_at TIMESTAMP,
    last_login TIMESTAMP
);
```

## Security
- All tokens encrypted at rest using Fernet
- HTTPOnly cookies for session management
- HTTPS only in production
- CORS configured for frontend domain
- Token refresh handled automatically

## API Changes
- All AI endpoints check for authenticated user
- User's Google token used for Gemini API calls
- 401 Unauthorized if not logged in
- Automatic token refresh if expired
