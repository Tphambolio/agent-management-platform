# Agent Management Platform - Verification Checklist

**Purpose**: Systematic verification to ensure extraction was successful and deployment is working

---

## 1. Verify Repository Extraction ✅

### Check Local Repository Exists
```bash
cd /home/rpas/agent-management-platform
git log --oneline | head -5
git remote -v
git branch -a
```

**Expected Output**:
- Commits: `108a2bf1`, `96523133`, `25e413a`
- Remote: `origin  https://github.com/Tphambolio/agent-management-platform.git`
- Branch: `counter-style-ui` tracking `origin/counter-style-ui`

### Verify Agent Data Backup
```bash
ls -lh /home/rpas/agent_data_backup/
sqlite3 /home/rpas/agent_data_backup/agents.db "SELECT COUNT(*) as agent_count FROM agents;"
```

**Expected**:
- Two .db files present
- SQL query returns number of agents (should be > 0)

---

## 2. Verify GitHub Repository

### Check GitHub Has Latest Code
```bash
curl -s https://api.github.com/repos/Tphambolio/agent-management-platform/branches/counter-style-ui \
  | python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"Latest commit: {data['commit']['sha'][:8]}\"); print(f\"Commit message: {data['commit']['commit']['message'][:60]}\")"
```

**Expected**:
- Commit: `108a2bf1`
- Message: "docs: add extraction and deployment status report"

### Verify Key Files Present on GitHub
```bash
for file in "Dockerfile.backend" "backend/app/streaming.py" "frontend/src/hooks/useAgentStreaming.js" "frontend/src/pages/AgentLab.jsx"; do
  echo -n "Checking $file: "
  curl -s "https://api.github.com/repos/Tphambolio/agent-management-platform/contents/$file?ref=counter-style-ui" \
    | python3 -c "import sys, json; data = json.load(sys.stdin); print('✅ Present' if 'name' in data else '❌ Missing')" 2>/dev/null || echo "❌ Missing"
done
```

**Expected**: All files show "✅ Present"

---

## 3. Verify Render Service Configuration

### Check Service Settings
```bash
# If you have Render API key:
curl -s -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.render.com/v1/services/srv-d4ahs6k9c44c738i3g5g" \
  | python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"Repo: {data.get('repo')}\"); print(f\"Branch: {data.get('branch')}\"); print(f\"Auto-deploy: {data.get('autoDeploy')}\"); print(f\"Dockerfile: {data['serviceDetails']['envSpecificDetails']['dockerfilePath']}\")"
```

**Expected**:
- Repo: `https://github.com/Tphambolio/agent-management-platform`
- Branch: `counter-style-ui`
- Auto-deploy: `yes`
- Dockerfile: `./Dockerfile.backend`

### Alternative: Manual Dashboard Check
1. Go to https://dashboard.render.com/web/srv-d4ahs6k9c44c738i3g5g
2. Check "Settings" tab:
   - Repository: `Tphambolio/agent-management-platform`
   - Branch: `counter-style-ui`
   - Root Directory: (empty)
   - Dockerfile Path: `./Dockerfile.backend`

---

## 4. Verify Deployment Status

### Check Recent Deployments
```bash
curl -s -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.render.com/v1/services/srv-d4ahs6k9c44c738i3g5g/deploys?limit=3" \
  | python3 -c "import sys, json; data = json.load(sys.stdin);
for d in data:
    print(f\"Deploy {d['id'][:10]}...\")
    print(f\"  Status: {d['status']}\")
    print(f\"  Commit: {d['commit']['id'][:8]} - {d['commit']['message'][:50]}\")
    print(f\"  Started: {d.get('startedAt', 'Not started')}\")
    print()"
```

**Look For**:
- Status: `live` (successful)
- Commit: `108a2bf1` or `96523133`
- No `build_failed` status

### Alternative: Check Deployment in Dashboard
1. Go to https://dashboard.render.com/web/srv-d4ahs6k9c44c738i3g5g
2. Click "Events" tab
3. Look for most recent deploy with status "Live"

---

## 5. Verify Backend Endpoints

### Test Health Endpoint
```bash
curl -s https://agent-platform-backend-3g16.onrender.com/health | python3 -m json.tool
```

**Expected**: `{"status": "healthy"}` or similar

### Test New Capabilities Endpoint (CRITICAL)
```bash
curl -s https://agent-platform-backend-3g16.onrender.com/api/capabilities | python3 -m json.tool
```

**Expected**:
```json
{
  "total_agents": <number>,
  "by_type": {
    "researcher": [...],
    "executor": [...]
  },
  "available_tools": [...]
}
```

**If 404**: Deployment hasn't happened yet or failed

### Test Sessions Endpoint
```bash
curl -s https://agent-platform-backend-3g16.onrender.com/api/sessions | python3 -m json.tool
```

**Expected**: `[]` (empty array) or list of sessions

### Test WebSocket Connection
```bash
# This will attempt WebSocket connection and should NOT get 404
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  "https://agent-platform-backend-3g16.onrender.com/ws/stream/test-session-id" 2>&1 | head -10
```

**Expected**: NOT "404 Not Found" (may get 400/426 upgrade error, that's OK - means endpoint exists)

---

## 6. Verify Frontend Integration

### Check Frontend Environment
```bash
curl -s https://frontend-pm8m5dxwk-travis-kennedys-projects.vercel.app/ | grep -o "Agent" | head -5
```

**Expected**: Should contain "Agent" text (means HTML loaded)

### Test Frontend → Backend Connection
1. Open browser: https://frontend-pm8m5dxwk-travis-kennedys-projects.vercel.app
2. Open browser DevTools (F12) → Console
3. Look for errors about `/api/capabilities`
4. Navigate to "Agent Lab" page

**Expected**:
- No 404 errors on `/api/capabilities`
- Agent Lab page loads
- Capabilities panel shows agent types

---

## 7. Verify Database Migration Status

### Check Migration Version (if you can SSH to Render)
```bash
# Via Render SSH or Shell
alembic current
```

**Expected**: Should show `db678df06b6a` or later

### Verify Tables Exist
```bash
# Via Render Shell
python3 -c "
from app.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print('Tables:', tables)
print('Has sessions:', 'sessions' in tables)
print('Has interaction_logs:', 'interaction_logs' in tables)
print('Has artifacts:', 'artifacts' in tables)
"
```

**Expected**:
- `sessions` table exists: True
- `interaction_logs` table exists: True
- `artifacts` table exists: True

---

## 8. End-to-End Test

### Create a Test Session
```bash
curl -X POST https://agent-platform-backend-3g16.onrender.com/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "test-agent",
    "initial_query": "Test query to verify system works"
  }' | python3 -m json.tool
```

**Expected**: Returns session object with `id`, `status`, `created_at`

### Retrieve Session
```bash
# Use session_id from above
curl -s https://agent-platform-backend-3g16.onrender.com/api/sessions/<session_id> | python3 -m json.tool
```

**Expected**: Returns same session with details

---

## 9. Verify No Data Loss

### Count Agents in Backup vs Live
```bash
echo "Backup count:"
sqlite3 /home/rpas/agent_data_backup/agents.db "SELECT COUNT(*) FROM agents;"

echo "Live count (if accessible):"
# Via Render Shell or after copying live DB
sqlite3 /path/to/live/agents.db "SELECT COUNT(*) FROM agents;"
```

**Expected**: Same count in both

### Verify Agent DNA Files
```bash
find /home/rpas/agent-management-platform -name "*.json" -path "*/.agents/dna/*" | wc -l
```

**Expected**: Should match number of agents previously created

---

## 10. Safety Checks

### Verify Wildfire Repo Untouched
```bash
cd /home/rpas/wildfire-simulator-v2
git status
git log --oneline | head -5
```

**Expected**:
- Status should be clean or show only expected changes
- Latest commits should NOT include agent-platform extraction

### Verify Separate Git Histories
```bash
echo "Wildfire repo:"
cd /home/rpas/wildfire-simulator-v2 && git log --oneline | grep "agent-management" | head -3

echo "Agent platform repo:"
cd /home/rpas/agent-management-platform && git log --oneline | head -3
```

**Expected**: Different commit histories, no overlap in extraction commits

---

## Automated Verification Script

Save this as `/home/rpas/verify_extraction.sh`:

```bash
#!/bin/bash

echo "=== AGENT PLATFORM EXTRACTION VERIFICATION ==="
echo

# 1. Local repo
echo "1. Checking local repository..."
cd /home/rpas/agent-management-platform 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✅ Local repo exists"
    git log --oneline | head -1 | sed 's/^/    /'
else
    echo "  ❌ Local repo NOT found"
fi
echo

# 2. Backup
echo "2. Checking data backup..."
if [ -f /home/rpas/agent_data_backup/agents.db ]; then
    echo "  ✅ agents.db backed up"
    ls -lh /home/rpas/agent_data_backup/*.db | sed 's/^/    /'
else
    echo "  ❌ Backup NOT found"
fi
echo

# 3. GitHub
echo "3. Checking GitHub repository..."
GITHUB_CHECK=$(curl -sf https://api.github.com/repos/Tphambolio/agent-management-platform)
if [ $? -eq 0 ]; then
    echo "  ✅ GitHub repo accessible"
    echo "$GITHUB_CHECK" | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'    Branch: {data.get(\"default_branch\")}')"
else
    echo "  ❌ GitHub repo NOT accessible"
fi
echo

# 4. Backend health
echo "4. Checking backend health..."
HEALTH=$(curl -sf https://agent-platform-backend-3g16.onrender.com/health)
if [ $? -eq 0 ]; then
    echo "  ✅ Backend responding on /health"
else
    echo "  ⚠️  Backend NOT responding"
fi
echo

# 5. New endpoints
echo "5. Checking new endpoints..."
CAPABILITIES=$(curl -sf https://agent-platform-backend-3g16.onrender.com/api/capabilities)
if [ $? -eq 0 ]; then
    echo "  ✅ /api/capabilities LIVE!"
    echo "$CAPABILITIES" | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'    Total agents: {data.get(\"total_agents\", 0)}')" 2>/dev/null || echo "    (endpoint responding)"
else
    echo "  ❌ /api/capabilities NOT FOUND (deployment may still be in progress)"
fi
echo

echo "=== VERIFICATION COMPLETE ==="
```

### Run Verification
```bash
chmod +x /home/rpas/verify_extraction.sh
/home/rpas/verify_extraction.sh
```

---

## Success Criteria

All of these must be TRUE:
- ✅ Local repo exists at `/home/rpas/agent-management-platform`
- ✅ GitHub repo has latest code (commit `108a2bf1`)
- ✅ Database files backed up (68KB + 92KB)
- ✅ Render service points to new repo + `counter-style-ui` branch
- ✅ `/health` endpoint responds
- ✅ `/api/capabilities` endpoint responds (NOT 404)
- ✅ `/api/sessions` endpoint responds
- ✅ Frontend loads without errors
- ✅ Agent count in backup matches expected
- ✅ Wildfire repo unchanged

---

## Troubleshooting

### If `/api/capabilities` returns 404:
1. Check Render deployment status (Dashboard → Events)
2. Look for build errors in logs
3. Verify `counter-style-ui` branch is being deployed
4. Check if `main.py` has the new endpoints in deployed code

### If Build Fails:
1. Check Dockerfile.backend has correct paths (no `agent-management-platform/` prefix)
2. Verify requirements.txt is accessible
3. Check Render logs for specific error

### If Data Missing:
1. Restore from `/home/rpas/agent_data_backup/`
2. Copy .db files to backend directory
3. Run migrations: `alembic upgrade head`

---

**Last Updated**: November 18, 2025
**Status**: Awaiting deployment completion for final verification
