# Gemini API Integration Setup Guide

**Status**: Code deployed, awaiting API key configuration  
**Commit**: `89cf0854` - Gemini integration complete

---

## What's Been Done ✅

1. **Created Session Processor** (`backend/app/session_processor.py`)
   - Processes user queries using Gemini API
   - Streams responses in real-time chunks
   - Logs all interactions to database
   - Updates session status on completion

2. **Updated WebSocket Endpoint** (`backend/app/main.py:966`)
   - Automatically triggers agent processing when client connects
   - Runs session processing in background task
   - Maintains WebSocket connection for streaming

3. **Graceful Degradation**
   - Works WITHOUT API key (shows helpful message)
   - Works WITH API key (full AI responses)

---

## How to Add GEMINI_API_KEY to Render

### Step 1: Get Your Free Gemini API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)

### Step 2: Add to Render Environment Variables

#### Option A: Via Render Dashboard (Recommended)

1. Go to: https://dashboard.render.com/web/srv-d4ahs6k9c44c738i3g5g
2. Click "Environment" tab
3. Click "Add Environment Variable"
4. Set:
   - **Key**: `GEMINI_API_KEY`
   - **Value**: `AIza...` (your API key)
5. Click "Save Changes"
6. Render will automatically redeploy (takes ~3-5 minutes)

#### Option B: Via Render CLI

```bash
# If you have Render CLI installed
render env set GEMINI_API_KEY=AIza...  # your actual key
```

---

## Testing After Deployment

### Test 1: WebSocket Connection (Without API Key)

The frontend will now successfully connect to the WebSocket and receive a helpful message:

```
I received your message: "Hello!"

However, the Gemini API is not configured. To enable AI responses, 
please set the GEMINI_API_KEY environment variable...
```

### Test 2: Full AI Chat (With API Key)

Once the API key is added, users will receive actual AI-generated responses:

1. Go to: https://frontend-travis-kennedys-projects.vercel.app/
2. Type a message like "Explain quantum computing"
3. Watch the response stream in real-time!

---

## Architecture Flow

```
User sends message
    ↓
Frontend → POST /api/sessions
    ↓
Session created in database
    ↓
Frontend → WebSocket /ws/stream/{session_id}
    ↓
WebSocket connects → Triggers session_processor.process_session()
    ↓
session_processor:
    1. Send "session_start" event
    2. Send "agent_thinking" event
    3. Call Gemini API (if available)
    4. Stream response in chunks (CHUNK events)
    5. Update session in database
    6. Send "session_complete" event
    ↓
Frontend receives streamed response in real-time
```

---

## What Will Happen Next

### Without GEMINI_API_KEY

✅ WebSocket connects successfully  
✅ Session is created  
✅ Helpful error message is sent  
❌ No AI responses

### With GEMINI_API_KEY

✅ WebSocket connects successfully  
✅ Session is created  
✅ Gemini processes the query  
✅ AI response streams in real-time  
✅ Session marked as completed  
✅ Full conversation history stored

---

## Monitoring Deployment

The code has been pushed to `counter-style-ui` branch and will auto-deploy.

Check deployment status:
```bash
# Monitor Render dashboard
https://dashboard.render.com/web/srv-d4ahs6k9c44c738i3g5g

# Or test endpoint
curl https://agent-platform-backend-3g16.onrender.com/health
```

Wait for the build to complete (~3-5 minutes), then test the WebSocket connection.

---

## Files Changed

- `backend/app/session_processor.py` - NEW: Gemini-powered agent executor
- `backend/app/main.py:966-988` - UPDATED: WebSocket endpoint triggers processing

---

## Next Steps

1. **Add GEMINI_API_KEY** to Render (instructions above)
2. **Wait for auto-deployment** (~3-5 min)
3. **Test the chat** at https://frontend-travis-kennedys-projects.vercel.app/
4. **Enjoy AI-powered conversations!** 🎉

---

## Troubleshooting

### WebSocket Still Fails to Connect

Check Render logs:
```bash
# View recent logs
https://dashboard.render.com/web/srv-d4ahs6k9c44c738i3g5g/logs
```

Look for:
- `✅ Gemini AI initialized (FREE tier)` - API key is working
- `⚠️ No GEMINI_API_KEY found - research disabled` - Need to add key

### "Message not found" or Database Errors

Run database migration:
```bash
# Via Render shell
alembic upgrade head
```

### Rate Limits

Gemini Free tier limits:
- 15 requests per minute
- 1,500 requests per day

If you hit limits, upgrade to paid tier at: https://ai.google.dev/pricing

---

**Last Updated**: November 19, 2025  
**Deployment**: Awaiting Render auto-deploy of commit `89cf0854`
