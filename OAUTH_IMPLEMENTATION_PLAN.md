# OAuth & User Credentials Implementation Plan

## Current Approach vs OAuth

### What We Have Now (System-Wide Keys):
- Single ANTHROPIC_API_KEY for all users
- Single BRAVE_API_KEY for all users
- All users share same quota/limits

### What We Can Build (Two Options):

## Option 1: User-Provided API Keys ⭐ (Recommended - Quick to implement)

**How it works:**
1. User visits app for first time
2. Modal popup: "To use Agent Lab, please provide your API keys"
3. User enters:
   - Anthropic API Key (required)
   - Google Gemini API Key (optional)
4. Keys are encrypted and stored per-user in database
5. Each request uses that user's keys

**Pros:**
- ✅ Quick to implement (1-2 hours)
- ✅ Each user has own quota
- ✅ No shared API costs
- ✅ Secure (encrypted storage)

**Cons:**
- ⚠️ Users need to get their own keys
- ⚠️ Slight friction on signup

**Implementation:**
- Backend: User credentials table with encryption
- Frontend: API key setup modal
- Middleware: Inject user's keys into requests

---

## Option 2: Full OAuth Flow (Better UX, More Complex)

### Google OAuth for Gemini

**How it works:**
1. User clicks "Sign in with Google"
2. OAuth popup → User authorizes
3. App gets OAuth token
4. Use token to call Gemini API on user's behalf

**Implementation:**
```python
# Backend OAuth endpoints
@app.get("/auth/google")
async def google_oauth_start():
    # Redirect to Google OAuth

@app.get("/auth/google/callback")
async def google_oauth_callback(code: str):
    # Exchange code for token
    # Store token per-user
```

### Anthropic API

**Problem:** Anthropic doesn't offer OAuth yet!

**Solutions:**
1. **Hybrid**: Use Google OAuth + user provides Anthropic key
2. **Shared Key**: Your backend provides Anthropic access to all users
3. **Wait**: Until Anthropic releases OAuth

---

## Recommended Implementation (Hybrid):

### Phase 1: User API Keys (This Week)
- Prompt users for API keys on first use
- Store encrypted per-user
- Simple, works today

### Phase 2: Add Google OAuth (Optional)
- "Sign in with Google" for Gemini access
- Still ask for Anthropic key separately
- Better UX for Gemini users

### Phase 3: Future (When Available)
- Full OAuth for all providers
- Zero API key entry required

---

## Code Structure:

```
backend/
  app/
    user_credentials.py ← Encryption & storage (DONE)
    routes/
      auth.py ← OAuth endpoints
      credentials.py ← API key management
    middleware/
      inject_user_keys.py ← Add keys to requests

frontend/
  src/
    components/
      APIKeySetup.jsx ← Modal for key entry
      GoogleOAuthButton.jsx ← OAuth flow
```

---

## Security Considerations:

1. **Encryption**: All keys encrypted at rest (Fernet)
2. **HTTPS Only**: No keys transmitted over HTTP
3. **Session-Based**: Keys never sent to frontend
4. **Per-Request**: Backend injects keys per request
5. **Audit Log**: Track key usage

---

## Next Steps:

1. ✅ Create user_credentials.py (DONE)
2. Add API endpoints for credential management
3. Create frontend modal for key entry
4. Add middleware to inject user keys
5. (Optional) Add Google OAuth

**Would you like me to:**
- **A)** Implement Option 1 (user-provided keys) now? (Quick, works today)
- **B)** Start with Google OAuth first? (More work, better UX)
- **C)** Both (OAuth for Google, manual for Anthropic)?

Let me know and I'll build it!
